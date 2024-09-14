from django.apps import AppConfig as AppCfg


class AppConfig(AppCfg):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    # ready() 是 Django 应用程序启动时执行初始化逻辑的地方。
    # 常见用途包括信号注册、扩展注册、模块导入、以及其他初始化任务。
    # 不要直接在 ready() 中进行数据库操作，避免循环导入问题。
    def ready(self):
        # 注册自定义扩展
        from utils.frame.drf_spectacular_external import CustomDrfSpectacularAuthenticationExtension
        CustomDrfSpectacularAuthenticationExtension('utils.frame.model_view_set.CustomBaseSessionAuthentication')
