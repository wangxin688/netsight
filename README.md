## Network Infrastructure Management System
> This project is inspired by Netbox, to separate backend and frontend development, built backend with FastAPI&Sqlalchemy and full async support for database, HTTP, etc.

## Notice
This project is still in development and not release a beta version. Changes will be made without
any notifications, especially for database E-R. It mostly depends on my spare time to update the
project, but any ideas or suggestions are welcome, you can create a git issue or contact me
at wangxin.jeffry@gmail.com to discuss the project.
As soon as I complete the beta version of the project, PR is welcome.


### More Lightweight
For our current env, we manage more than 50K+ network devices and VMS. it's hard to maintain with
such complex object relationships, also with bad performance.
For following features, are only my ideas and not related to the current environment, also, this project is built with interest outside of work.
1. remove tenant support, for the most common case we don't need multi-tenant support in
   a self-managed enterprise network. It will more simple and efficient for database relationship
2. remove virtual-chassis support, there are so many virtualization techs for the different vendors,
   like StackWise, VirtualChassis, IRF, stack, CSS, and regard all tec as a cluster for members.
3. remove device components objects like slot, console port, out-of-band port, power, fans, etc, and only keep interfaces with devices. you can extend this table with LLDP table and neo4j ORM to generate network topology, but it will not include in this project.
4. remove site_group, \I refuse to design a nested or combine a couple of sites within a group. It will make a huge challenge for operation, monitoring, automation, and data analysis. My suggestion is that make a very clear and standard, highly unified network architecture for a dedicated site, some things like Campus network v1.0, v2.0, DataCenter v1.0, and v2.0 with and following the rule to build the network.
5. remove some tables to lightweight the object relationship, and use the enum type to define some fields. (I know this will reduce the flexibility for different users. But the main goal for me is to build a system that supports a large-scale network simple and efficient without every detail in the network. So need compromised)
### More feature 
1. add the department to DCIM devices and  classification to DCIM site natively without extra custom fields
2. use ENUM type for constraints without id-mapping, which will be more efficient and simple
3. with more features with WLAN(later)
4. data analysis
5. integrate with downstream and upstream plugins
6. RBAC or ABAC?
   Personally, I think RBAC is enough for most case, ABAC is more powerful and flexible, but at the same time, brings complexity and need more effort from management in your organization. Maybe it's a good idea to integrate with Pycasbin for ABAC. But I don't have enough time to figure it out. 
7. unified log management with correlation-id for Gunicorn and hole project.
8. audit log with JSON format, very easy to integrate with Filebeat and Elasticsearch for metrics, tracing, and analysis.
9. x-request-id, x-process-time in header
10. python 3.10+ support, with full type-hint and Pydantic validation control


### How to start?
1. pull the project from GitHub
2. `chmod +x init.sh pre-push.sh` and  execute `init.sh`
3. execute `touch .env` in the project root path, and add environment variables, which define in `src/core/config.py Settings class`, you can always refer to Pydantic docs. also, I add some comments in this file.
4. set up one of the python virtual environments: venv or poetry env as you prefer
5. install requirements.txt 
6. execute `python3 src/init_app.py` to create superuser 
7. execute app: `python3 main.py` or install supervisor on Linux, the demo of the config file is already in the project.