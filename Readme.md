**代码实现步骤**
1.根据isbn或者关键字从restful api中获取json数据，见spider
2.建立对应的模型和视图模型，见model和view_model
3.表单的实现和验证，见validator
4.用户注册登录的加密和验证，见user
5.相关视图函数业务的实现，添加礼物清单-->添加心愿清单-->索要礼物-->发送邮件
6.用户忘记密码，和发送邮件，生成token，从新链接到网站主页
7.交易业务的完成--较难

重要知识：
1.blueprint
2.contextmanager
3.login_required
4.线程隔离，app和request
5.model中的通用base.py