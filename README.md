## Background
This project draws inspiration from Netbox, incorporating significant changes to better support built-in automation systems for netdevops. Having worked as a network engineer for over 5 years, I've managed more than 50,000 network devices, including but not limited to switches, routers, firewalls, SD-WAN, OVS, SDN, from various vendors in enterprise LAN/WAN/WLAN, and datacenter environments. Our team, consisting of more than 40 people, has been using Netbox for over 4 years. However, reaching a consensus on standards has proven challenging due to the lack of validations and limitations of netbox.

While Netbox is undoubtedly a great and powerful tool, in my personal view, some of its data structures are too complex for efficient automation. It's better suited for modeling your network rather than serving as a primary tool for automation."

Based on this foundation, I plan to launch a completely new project and build on top of FastAPI with pydantic. The new product will focus on simplifying data structures, providing more robust validation capabilities, and better supporting network automation processes. By optimizing these aspects, my goal is to offer a more user-friendly and efficient tool for netdevops, enabling them to smoothly devise and execute standardized network operational procedures.

## Architecture
![netsight-arch drawio](https://github.com/wangxin688/netsight/assets/36665036/3649d2ff-fdae-42aa-8fc8-0c74e9dc0473)


## Introducation
Netsight aims to serve as a comprehensive network full life-cycle automation system. It is constructed on top of FastAPI, empowered by Pydantic to ensure robust data validation and limitations. This platform is designed to offer a multitude of features catering to the following functions:

- Network Source of Truth:
Netsight establishes itself as the authoritative source of truth for your network infrastructure, providing a centralized and accurate repository of network data.
- Network Configuration Management:
The platform facilitates efficient and organized management of network configurations, allowing for seamless updates and changes across the network infrastructure.
- Intent-Based Networking:
Netsight embraces intent-based networking, enabling network administrators to express their desired outcomes, allowing the system to autonomously translate these intentions into actionable network configurations.
- Network Inventory Autodiscovery:
Automated network inventory discovery ensures that the platform stays up-to-date with the latest additions or modifications to the network, providing a dynamic and accurate representation of the network inventory.
- Network Topology Autodiscovery:
Netsight employs automatic topology discovery to visualize and understand the intricate relationships and interconnections within the network, promoting a comprehensive understanding of the network architecture.
- Assurance for Monitoring and Alerting:
The platform includes robust assurance mechanisms for continuous monitoring and timely alerting, ensuring proactive detection of anomalies and potential issues within the network.
- Change Management:
Netsight introduces a streamlined change management process, facilitating controlled and documented modifications to the network. This ensures transparency, accountability, and the ability to roll back changes if necessary.
By incorporating these features, Netsight aims to providing a powerful and user-friendly solution for network engineers, contributing to a more reliable and automated network management experience.


## Notice
This project is currently in the development phase, and a beta version has not been released yet. Changes will be implemented without prior notifications, with a particular emphasis on modifications to the database design. The project's progress is primarily reliant on my personal time and interests. While I aim to update the project whenever possible, it's important to note that development decisions, especially those related to feature additions, are primarily guided by my extensive engineering experience.

Given the evolving nature of the project, any ideas or suggestions are highly encouraged and welcomed. Users are invited to create Git issues to initiate discussions and contribute to the project's enhancement. Please be aware that updates may occur based on my availability and may not be communicated in advance, highlighting the dynamic and iterative nature of the development process.


## Features
### Changes
- Omitting tenant support:
In the context of a self-managed enterprise network, multi-tenant support is often unnecessary for the typical use case. By removing this feature, we aim to streamline and enhance the efficiency of database relationships.
> Some personal thoughts about multi-tenant:
> **Data Security**: When considering multiple tenancy, data security is a crucial concern. Using logical isolation based on identifiers, such as IDs, within the same database inevitably introduces security risks. On the other hand, physical isolation enhances data security but adds overhead for sharing some common data, leading to increased development and operational costs. A balanced compromise is leveraging PostgreSQL's schema-based approach for data isolation, but this may require additional development effort.
**Necessity**: The motivation behind designing this solution is driven solely by personal interest, without considering commercial requirements. In self-managed enterprise networks and data centers, the majority of scenarios may not necessitate multi-tenancy support. If there is a need for data-level isolation, exploring options like a data warehouse to provide Attribute-Based Access Control (ABAC) capabilities could be considered. Moreover, at the foundational level, if future extensions for multi-tenancy (based on ID-based isolation) are required, they can be implemented with ease.
- Eliminating regions:
The intention is to utilize site_group for site management, incorporating configuration inheritance. This adjustment simplifies the structure and improves overall manageability.
- Constraining location tree depth:
 Recognizing the impracticality of limitless depth in Netbox's location tree, we propose implementing a reasonable limit. This modification seeks to enhance the usability and organization of location-related data.
- Abandoning virtual-chassis support:
Given the diverse virtualization technologies employed by different vendors (e.g., StackWise, VirtualChassis, IRF, stack, CSS), treating all these technologies as a cluster for members provides a more versatile approach. Handling stack configurations for automation becomes less complex when choosing between treating devices as physical or logical entities.
- Introducing device entity:
 Managing devices in a logical manner, as opposed to treating them as assets, adds a layer of simplicity and clarity to device management within the system.
- Consolidating device components:
Simplifying the data model by removing device components such as slots, console ports, out-of-band ports, power, fans, etc., and retaining only interfaces with devices streamlines the representation of network elements.
- Streamlining object relationships:
Removing select tables and utilizing enum types to define certain fields contributes to a lighter-weight object relationship model. While acknowledging that this may reduce flexibility for some users, the primary goal is to construct a system that efficiently supports large-scale networks without necessitating exhaustive details for every network element. This compromise aims to strike a balance between simplicity and usability.
- And a lot of changes will be introuduced later
### New Features(later)


## StartUp
> current only backend is support with docker compose
> if docker compose not installed, please install docker compose first.

```shell
# if you want customize ENVIRONMENT for backend, such a DATABASE_USER, PASSWORD
# just replace environment in docker-compose.yaml

docker compose up -d
# if code update:
# run `docker-compose up -d --no-deps --build backend` to upgrade to latest
docker ps
```
### OpenAPI
1. swagger: http://localhost:8000/api/docs
2. redoc: http://localhost:8000/api/redoc
3. elements: http://localhost:8000/api/elements
### Built-in(but very limited) Admin Dashboard
Admin Page: http://localhost:8000/admin/login  demo_user/password: admin@netsight.com/admin

## Development Guide
### install Rye for python project management
> full step: https://rye.astral.sh/guide/installation/
```shell
cd backend
curl -sSf https://rye.astral.sh/get | bash

# install packages
rye sync

# please comment backend part in docker-compose.yaml
# pull up postgresql and redis
docker compose up -d

#
alembic upgrade head
python deploy/init_metadata.py
python src/__main__.py

# if you want run app in debug mode, run following command
uvicorn src.app:app --reload

```

## HELP WANTED for frontend development
> Because of my personal time limitation, I don't have too much time for frontend side development.(now I only add a very simple admin dashboard to show data. I have no plans to invest too much time on that)
> On the first stage, I will focus on backend development, especially extend network related features.
> If anyone is interested with frontend part I will be happy with contributions. (Vue3/React are both accepted ^_^, React is much more recommend).
