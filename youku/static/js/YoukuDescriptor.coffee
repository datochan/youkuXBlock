## coding: utf-8

class @YoukuDescriptor extends XModule.Descriptor
    constructor: (runtime, element, initArgs) ->
        @runtime = runtime
        @el = $(element)
        $(element).data 'name', 'YoukuDescriptor'
        return @

    $: (selector) ->
        $(selector, @el)

    save: ->
        code_context = {
            display_name: @el.find('input[name=display_name]').val(),
            file_id: @el.find('input[name=file_id]').val(),
            app_id: @el.find('input[name=app_id]').val(),
            width: @el.find('input[name=width]').val(),
            height: @el.find('input[name=height]').val()
        }

        {
            data: JSON.stringify(code_context),
            metadata: code_context
        }