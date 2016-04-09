#youkuXBLock 
by wwj718:<wuwenjie718@gmail.com>

modify by datochan:<datochan@qq.com>

优酷开发平台：http://open.youku.com/

# 改动
* 功能没有任何修改，只是借wwj718的这个例子说明基于capa的方式编写xblock的方法。
* 与wwj718的源代码相比，只是换了种写法，其它方面没有任何变动。
* 感觉基于capa的方式编写xblock代码更加简单一些。

#安装（平台级别的设置）
*  sudo su edxapp -s /bin/bash
*  cd ~
*  source edxapp_env
*  pip install git+https://github.com/wwj718/youkuXBlock.git
*  在/edx/app/edxapp/cms.envs.json 添加 `"ALLOW_ALL_ADVANCED_COMPONENTS": true,` 到FEATURES
*  sudo /edx/bin/supervisorctl restart edxapp:

#在studio中设置(课程级别的设置)
进入到"Settings" ⇒ "Advanced Settings",将"youku"添加到Advanced Module List

#使用方法（结合优酷）
参考wwj718的文章:[在edx中使用优酷视频服务](http://wwj718.github.io/edx-use-youku.html)
