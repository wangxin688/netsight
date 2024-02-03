### Background
This project draws inspiration from Netbox, incorporating significant changes to better support built-in automation systems for netdevops. Having worked as a network engineer for over 5 years, I've managed more than 50,000 network devices, including but not limited to switches, routers, firewalls, SD-WAN, OVS, SDN, from various vendors in enterprise LAN/WAN/WLAN, and datacenter environments. Our team, consisting of more than 40 people, has been using Netbox for over 4 years. However, reaching a consensus on standards has proven challenging due to the lack of validations and limitations of netbox.

While Netbox is undoubtedly a great and powerful tool, in my personal view, some of its data structures are too complex for efficient automation. It's better suited for modeling your network rather than serving as a primary tool for automation."

Based on this foundation, I plan to launch a completely new project and build on top of FastAPI with pydantic. The new product will focus on simplifying data structures, providing more robust validation capabilities, and better supporting network automation processes. By optimizing these aspects, my goal is to offer a more user-friendly and efficient tool for netdevops, enabling them to smoothly devise and execute standardized network operational procedures.

### Architecture
![netsight-arch drawio](https://github.com/wangxin688/netsight/assets/36665036/3649d2ff-fdae-42aa-8fc8-0c74e9dc0473)


### Introducation
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
