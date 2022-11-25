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
4. remove site_group, as a network operation architect, I personally refuse to design an nested or      combine couple sites within a group. It will make a huge challenge for operation, monitoring, automation and data analysis. My suggestions is that make a very clear and standard, highly unified network architecture for a dedicated site, somethings like Campus network v1.0, v2.0, DataCenter v1.0, v2.0 with and following the rule to build network.
### More feature 
1. add department to dcim devices and  classification to dcim site natively without extra custom fields
2. use ENUM type for constraints without id-mapping, which will be more efficient and simple
