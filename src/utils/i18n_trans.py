locale = {
    "en_US": {
        "netsight": {
            "success": "success",  # 0
            "validation_error": "params or request body is invalid, please check your request data",  # 422
            "server_error": "Internal Server Error, request_id: {request_id}, please escalate to netsight administrators",  # 500
            "in_process": "Request not completed, in processing",  # 202
            "not_found": "Requested object {object} with {field}: {value} not found",  # 404
            "already_exists": "Requested object {object} with {field}: {value} already exists",  # 409
        },
        "auth": {
            "token_invalid_not_provided": "Authenticated failed: Bearer token invalid or not provide",  # 401
            "token_expired": "Authenticated failed: Bearer token expired",  # 402
            "refresh_token": "Authenticated failed: Bearer token is refresh token",  # 411
            "permission_denied": "Permission Denied: Privilege limited, Operation not permit",  # 403
            "incorrect_password": "Login failed: Password is incorrect",  # 10003
        },
        "dcim": {
            "site": {
                "name_not_found": "site {name} not found",
                "id_not_found": "site {name} not found",
            },
        },
        "ipam": {},
        "circuit": {},
    },
    "zh_CN": {
        "netsight": {
            "success": "成功",  # 0
            "validation_error": "路径参数或请求体数据校验错误, 请确认请求参数是否合法",  # 1
            "server_error": "服务器内部错误, 请求ID:{request_id}, 请将问题升级至平台管理员",  #
            "in_process": "请求未完成, 处理中",  # 202
            "not_found": "{object}: {field} {value}未找到}",  # 404
            "already_exists": "{object}: {field}: {value}已存在",  # 409
        },
        "auth": {
            "token_invalid_not_provided": "认证失败, Bearer token无效或未提供",
            "token_expired": "认证失败, Bearer token已过期",
            "refresh_token": "认证失败, Bearer token为refresh token",
            "permission_denied": "权限不足, 当前操作不允许",
            "incorrect_password": "登录失败, 密码错误",
        },
        "dcim": {
            "site": {
                "name_not_found": "site {name} not found",
                "id_not_found": "site {name} not found",
            },
        },
        "ipam": {},
        "circuit": {},
    },
}
