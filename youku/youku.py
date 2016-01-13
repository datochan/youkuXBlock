#coding=utf-8
#author: wwj718
#author_email: wuwenjie718@gmail.com
#author_blog: wwj718.github.io

""" youkuXBlock main Python class"""

import json
import os
import logging

from xblock.fields import Scope, String, Integer
from xblock.fragment import Fragment
from mako.template import Template
from django.utils.translation import ugettext as _
from xmodule.capa_base import ComplexEncoder
from xmodule.exceptions import ProcessingError, NotFoundError
from xmodule.progress import Progress
from xmodule.x_module import XModule, module_attr
from xmodule.capa_module import CapaFields, RawDescriptor, CapaMixin

import sys

reload(sys)
sys.setdefaultencoding('utf8')
_ = lambda text: text

log = logging.getLogger("edx.youku_components")


class YoukuFields(CapaFields):
    '''
    Icon of the XBlock. Values : [other (default), video, problem]
    '''
    icon_class = "video"

    '''
    Fields
    '''
    display_name = String(display_name="Display Name",
                          default="youku player",
                          scope=Scope.settings,
                          help="This name appears in the horizontal navigation at the top of the page.")

    app_id = String(display_name="video client_id",
                    default="youku",
                    scope=Scope.content,  # Scope.content和Scope.settings不同在于，(可见性)本课多处可用
                    help="The  client_id for your video.")

    file_id = String(display_name="video vid",
                     default="youku",
                     scope=Scope.content,  # Scope.content和Scope.settings不同在于，(可见性)本课多处可用
                     help="The vid for your video.")

    width = Integer(display_name="Video player width",
                    default="560",
                    scope=Scope.content,
                    help="The width for your video player.")
    height = Integer(display_name="Video player height",
                     default="320",
                     scope=Scope.content,
                     help="The height for your video player.")


class YoukuMixin(YoukuFields, CapaMixin):
    pass


class YoukuModule(YoukuMixin, XModule):
    """
    主观题的视图
    """
    js_module_name = "YoukuModule"
    mako_template = "/static/html/youku_view.html"

    def get_html(self):
        mako_template = Template(filename=os.path.dirname(__file__) + self.mako_template)

        content = {
            'name': self.display_name,
            'html': self.lcp.get_html(),
            'weight': self.weight
        }

        return mako_template.render_unicode(problem=content,
                                            xblock_id=self.location.block_id,
                                            app_id=self.app_id,
                                            file_id=self.file_id,
                                            width=self.width,
                                            height=self.height)

    def student_view(self, context):
        frag = Fragment(self.get_html())
        # frag.add_javascript_url(self.runtime.local_resource_url(self, "/static/js/h5connect.js"))
        frag.add_javascript_url(self.runtime.local_resource_url(self, "/static/js/youku_api.js"))

        mako_template = Template(filename=os.path.dirname(__file__)+"/static/js/YoukuModule.js")
        frag.add_javascript(mako_template.render_unicode(xblock_id=self.location.block_id,
                                                         app_id=self.app_id,
                                                         file_id=self.file_id))

        frag.initialize_js("YoukuModule")

        return frag

    def handle_ajax(self, dispatch, data):
        """
        This is called by courseware.module_render, to handle an AJAX call.

        `data` is request.POST.

        Returns a json dictionary:
        { 'progress_changed' : True/False,
          'progress' : 'none'/'in_progress'/'done',
          <other request-specific values here > }
        """
        handlers = {
            'problem_get': self.get_problem,
            'problem_check': self.check_problem,
            'problem_reset': self.reset_problem,
            'problem_save': self.save_problem,
            'problem_show': self.get_answer,
            'score_update': self.update_score,
            'input_ajax': self.handle_input_ajax,
            'ungraded_response': self.handle_ungraded_response
        }

        _ = self.runtime.service(self, "i18n").ugettext

        generic_error_message = _(
            "We're sorry, there was an error with processing your request. "
            "Please try reloading your page and trying again."
        )

        not_found_error_message = _(
            "The state of this problem has changed since you loaded this page. "
            "Please refresh your page."
        )

        if dispatch not in handlers:
            return 'Error: {} is not a known capa action'.format(dispatch)

        before = self.get_progress()

        try:
            result = handlers[dispatch](data)

        except NotFoundError as err:
            _, _, traceback_obj = sys.exc_info()  # pylint: disable=redefined-outer-name
            raise ProcessingError, (not_found_error_message, err), traceback_obj

        except Exception as err:
            _, _, traceback_obj = sys.exc_info()  # pylint: disable=redefined-outer-name
            raise ProcessingError, (generic_error_message, err), traceback_obj

        after = self.get_progress()

        result.update({
            'progress_changed': after != before,
            'progress_status': Progress.to_js_status_str(after),
            'progress_detail': Progress.to_js_detail_str(after),
        })

        return json.dumps(result, cls=ComplexEncoder)


class YoukuDescriptor(YoukuFields, RawDescriptor):
    module_class = YoukuModule

    has_score = True
    template_dir_name = "problem"
    js_module_name = "YoukuDescriptor"
    mako_template = "/static/html/youku_edit.html"

    def get_html(self):
        mako_template = Template(filename=os.path.dirname(__file__)+self.mako_template)

        return mako_template.render_unicode(display_name=self.display_name,
                                            xblock_id=self.location.block_id,
                                            app_id=self.app_id,
                                            file_id=self.file_id,
                                            width=self.width,
                                            height=self.height)

    def studio_view(self, _context):
        """
        The secondary view of the XBlock, shown to teachers
        when editing the XBlock.
        """
        frag = Fragment(self.get_html())


        mako_template = Template(filename=os.path.dirname(__file__)+"/static/js/YoukuDescriptor.js")
        frag.add_javascript(mako_template.render_unicode(xblock_id=self.location.block_id))

        frag.initialize_js("YoukuDescriptor")

        return frag

    def handle_ajax(self, dispatch, data):
        """
        This is called by courseware.module_render, to handle an AJAX call.

        `data` is request.POST.

        Returns a json dictionary:
        { 'progress_changed' : True/False,
          'progress' : 'none'/'in_progress'/'done',
          <other request-specific values here > }
        """
        handlers = {
            'problem_get': self.get_problem,
            'problem_check': self.check_problem,
            'problem_reset': self.reset_problem,
            'problem_save': self.save_problem,
            'problem_show': self.get_answer,
            'score_update': self.update_score,
            'input_ajax': self.handle_input_ajax,
            'ungraded_response': self.handle_ungraded_response
        }

        _ = self.runtime.service(self, "i18n").ugettext

        generic_error_message = _(
            "We're sorry, there was an error with processing your request. "
            "Please try reloading your page and trying again."
        )

        not_found_error_message = _(
            "The state of this problem has changed since you loaded this page. "
            "Please refresh your page."
        )

        if dispatch not in handlers:
            return 'Error: {} is not a known capa action'.format(dispatch)

        before = self.get_progress()

        try:
            result = handlers[dispatch](data)

        except NotFoundError as err:
            _, _, traceback_obj = sys.exc_info()  # pylint: disable=redefined-outer-name
            raise ProcessingError, (not_found_error_message, err), traceback_obj

        except Exception as err:
            _, _, traceback_obj = sys.exc_info()  # pylint: disable=redefined-outer-name
            raise ProcessingError, (generic_error_message, err), traceback_obj

        after = self.get_progress()

        result.update({
            'progress_changed': after != before,
            'progress_status': Progress.to_js_status_str(after),
            'progress_detail': Progress.to_js_detail_str(after),
        })

        return json.dumps(result, cls=ComplexEncoder)

    # Proxy to CapaModule for access to any of its attributes
    answer_available = module_attr('answer_available')
    check_button_name = module_attr('check_button_name')
    check_button_checking_name = module_attr('check_button_checking_name')
    check_problem = module_attr('check_problem')
    save_problem = module_attr('save_problem')
    choose_new_seed = module_attr('choose_new_seed')
    closed = module_attr('closed')
    get_answer = module_attr('get_answer')
    get_problem = module_attr('get_problem')
    get_problem_html = module_attr('get_problem_html')
    get_state_for_lcp = module_attr('get_state_for_lcp')
    handle_input_ajax = module_attr('handle_input_ajax')
    handle_problem_html_error = module_attr('handle_problem_html_error')
    handle_ungraded_response = module_attr('handle_ungraded_response')
    is_attempted = module_attr('is_attempted')
    is_correct = module_attr('is_correct')
    is_past_due = module_attr('is_past_due')
    is_submitted = module_attr('is_submitted')
    lcp = module_attr('lcp')
    make_dict_of_responses = module_attr('make_dict_of_responses')
    new_lcp = module_attr('new_lcp')
    publish_grade = module_attr('publish_grade')
    rescore_problem = module_attr('rescore_problem')
    reset_problem = module_attr('reset_problem')
    set_state_from_lcp = module_attr('set_state_from_lcp')
    should_show_check_button = module_attr('should_show_check_button')
    should_show_reset_button = module_attr('should_show_reset_button')
    should_show_save_button = module_attr('should_show_save_button')
    update_score = module_attr('update_score')
