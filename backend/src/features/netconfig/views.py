from sqladmin import ModelView

from src.features.netconfig.models import AuthCredential, BaseLineConfig, JinjaTemplate, TextFsmTemplate


class BaseLineConfigView(ModelView, model=BaseLineConfig):
    name = "Baseline Configuration"
    name_plural = "Baseline Configurations"
    category = "Network Configuration"
    column_list = [
        BaseLineConfig.aaa_server,
        BaseLineConfig.dhcp_server,
        BaseLineConfig.dns_server,
        BaseLineConfig.ntp_server,
        BaseLineConfig.syslog_server,
        BaseLineConfig.netflow_server,
    ]


class AuthCredentialView(ModelView, model=AuthCredential):
    name = "Auth Credential"
    name_plural = "Auth Credentials"
    category = "Network Configuration"
    column_list = [
        AuthCredential.cli,
        AuthCredential.snmpv2_community,
        AuthCredential.snmpv3,
        AuthCredential.created_at,
        AuthCredential.updated_at,
    ]


class JinjaTemplateView(ModelView, model=JinjaTemplate):
    name = "Jinja Template"
    name_plural = "Jinja Templates"
    category = "Network Configuration"
    column_list = [
        JinjaTemplate.name,
        JinjaTemplate.template,
        JinjaTemplate.platform,
        JinjaTemplate.created_at,
        JinjaTemplate.updated_at,
    ]


class TextFsmTemplateView(ModelView, model=TextFsmTemplate):
    name = "TextFSM Template"
    name_plural = "TextFSM Templates"
    category = "Network Configuration"
    column_list = [
        TextFsmTemplate.name,
        TextFsmTemplate.template,
        TextFsmTemplate.platform,
        TextFsmTemplate.created_at,
        TextFsmTemplate.updated_at,
    ]
