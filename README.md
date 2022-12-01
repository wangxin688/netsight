## Network Infrastrucure Management System
> This project is inspired by Netbox, in order to separate backend and frontend development, built backend with FastAPI&Sqlalchemy and full async support and 
> for database, http and etc.

### More Lightweight
For our current env, we management more than 50K+ network devices and vms. it's hard to maintain with
such complex object relationship, also with bad performance.
For following features, they are only my personal ideas and not related to current environment, also, this project is built with interest outside of work.
1. remove tenant support, for most common case we don't need multi-tenant support in
   self-manage enterprise network. It will more simple and efficient for database relationship
2. remove virtual-chassis support, there are so many virtualization tec for different vendor,
   like stackwise, virtual-chassis, IRF, stack, CSS, regard all tec as a cluster for members.
3. remove device components object like slot, console port, out-of-band port, power, fans and etc, only keep interface with device. you can extend this table with LLDP table and neo4j orm to generate network topology, but it will not include in this project.
4. remove site_group, \I personally refuse to design an nested or combine couple sites within a group. It will make a huge challenge for operation, monitoring, automation and data analysis. My suggestions is that make a very clear and standard, highly unified network architecture for a dedicated site, somethings like Campus network v1.0, v2.0, DataCenter v1.0, v2.0 with and following the rule to build network.
### More feature 
1. add department to dcim devices and  classification to dcim site natively without extra custom fields
2. use ENUM type for constraints without id-mapping, which will be more efficient and simple
3. with more feature with WLAN(later)
4. data analysis
5. integrate with downstream and upstream plugins
6. RBAC or ABAC ?
   Personally I think rbac is enough for most case, ABAC is more powerful and flexible, in the same time, brings complex and need more efforts for management in your organization. Maybe it's a good idea to integrate with pycasbin for ABAC. But I don't have enough time to figure it out. 
7. unified log management with correlation-id for gunicorn and hole project.
8. audit log with json format, very easy to integrate with filebeat and elasticsearch for metrics, tracing and analysis.
9. x-request-id, x-process-time in header


### How to start?
1. pull project from github
2. `chmod +x init.sh pre-push.sh` and  execute `init.sh`
3. execute `touch .env` in project root path, add environment variables, which define in `src/core/config.py Settings class`, you can always refer pydantic docs. also I add some comments in this file.
4. set up one of python virtual environment: venv or poetry env as you prefer
5. install requirements.txt 
6. execute `python3 src/init_app.py` to create superuser 
