# Product summary

| Product Name               | Ask ID | Techical Lead | PMO Lead| Cloud Platform    | Business Unit     |
|:--------------------------:|:------:|--------------:|--------:|:-----------------:|:-----------------:|
|Contract Tool (Azure Based) |        |               |         | Azure             | OptumRx           |

## Table of Contents
* Section 1: General                      
* Section 2: Data Governance              
* Section 3: Code Delivery and Management 
* Section 4: Architecture Summary         
* Section 5: Network Summary              
* Section 6: Security Criteria            

## Section 1: General
### Description
This document outlines the intake request for the development of the Contract Tool MVP in the Azure public cloud environment. The Contract Tool will provide a user-friendly interface for answering key questions related to pharma contracts, improving efficiency and accessibility to critical information. This initial MVP focuses on delivering core functionality while leveraging Azure services for scalability and cost-effectiveness.

### Business Segment Chief Architect Awareness
* proof of approval on mail from the Business Segment Chief Architect - **Required**
* Business Segment Chief Architect - **Required**

### User Details
*	Users are primarily internal OptumRx personnel
*	Potentially expanding to other internal Optum business units in the future.
* Expected activity (total population, Daily active Users, new users per month)?
  * For the MVP phase, limited user base with projected [**Required Insert Estimated Number**] daily active users.
* Authenticating and authorizing
  * Users will be authenticated via [**Required Specify Authentication Method - e.g., Azure Active Directory**].
  * Access control will be role-based with different permission levels for viewing, uploading, and managing contracts.

### Teams
* Contract Management
*	Data Analytics
*	Business Operations

### Workload Placement use case
* **Commercial Initiative**: This solution has the potential to support external clients in the future, streamlining interactions with pharmaceutical companies.
* **Data\User Gravity**: Minimal data transfer required outside of Optum's existing systems. User base primarily internal, minimizing external network dependency.
* **Critical Emerging Technology**: Leverages Azure's cloud-native technologies including AI/ML services and serverless functions for efficient scaling and resource management.
* **Requires emerging public cloud technology**: The data needs to be hosted in Azure so that other teams with valid workload placement use cases can make use of the data in their applications.
* **Using emerging technologies**
  * Azure OpenAI Service – LLM Models GPT 4 
  * Azure Functions
  * Azure Storage Accounts
  * Azure App Service
  * Azure Container Registry
  * Azure Container Apps
  * Azure API Management
  * Azure DevOps
  * Application Gateway

### Existing workload displacement & cost recovery
* Perceived amount of cost savings over time: Projected cost savings through increased efficiency in:
  * Contract retrieval and analysis
  * Reduction in manual data processing
  * Streamlined information sharing

### Summary
Leveraging the Azure cloud for the Contract Tool MVP offers a compelling solution due to its cost-effectiveness, scalability, and potential to streamline critical business processes within OptumRx.

### Alternatives
Developing and hosting the Contract Tool on-premises was considered. However, this approach would require significant upfront investment in hardware and software infrastructure, and it would lack the scalability and flexibility offered by the Azure cloud environment.

### External API documentation
Reference:

### Product Summary Circumstances and Exceptions

## Section 2: Data Governance 

### Data Details
### Intended Data Use 
### Upstream Data Interfaces and Sources
### Source Data Sets
### Downstream Targets 

## Section 3: Code Delivery and Management 

### Infrastructure as Code
### CI/CD
*	CI/CD Platform: We will utilize [Specify CI/CD Platform – e.g., Azure DevOps] to manage the continuous integration and deployment of the application. This will involve automated builds, testing, and deployments to different environments (dev, test, prod)
*	[Optional] Include diagram for visual representation of your CI/CD pipeline
### Code Delivery and Management Circumstances and Exceptions

## Section 4: Architecture Summary

### Architecture Overview
| Component               | Usage |
|:------------------------|:-------|
|Azure Blob Storage | Storage for raw contract documents |
|Azure Functions	| Processing contract uploads, metadata extraction, triggering AI indexing |
|Azure Cognitive Search	| Indexing and enabling AI-powered search capabilities on contract content |
|Azure OpenAI Service (GPT-4)	| Large language model for generating natural language responses to user queries |
|ReactJS Web Application	| Front-end user interface for interacting with the Contract Tool |
|[Insert other relevant Azure services here] | [Describe their purpose] |

### Architecture Circumstances and Exceptions

## Section 5: Network Summary
### Network Summary Diagram
| Connection Info/Direction | Network Ports | Purpose |
|:------------------------|:----------------|:--------|
|Inbound from Internet	| 443 (HTTPS)	          | Access to web application for authenticated users |
|Internal	              | [Specify port ranges]	| Communication between application components (e.g., web app to backend services) |
|[Add other relevant communication flows as needed] |                  |                | 

### Network Circumstances and Exceptions 

## Section 6: Security Criteria
### Security Considerations
### EIS Security Intent Review
### SCG Technical Controls
| CSP Requirement Category	| Req ID	| Functional Requirement | Consumer Responsibility |
|:--------------------------|:--------|:-----------------------|:------------------------|
|Encryption	| 2.1	| Key Strength: Cloud native functionality protecting confidentiality, authenticity, and integrity of data; data must be encrypted at rest and in motion | Data at rest will be encrypted using Azure Storage Service Encryption or customer-managed keys in Azure Key Vault. Transport Layer Security (TLS) will be used for encryption in transit |
|Encryption	| 2.2	| Key Management: Optum Technology will manage keys and certificates associated with encryption | Azure Key Vault will be our primary key management solution for managing and rotating keys |
|[Add other relevant categories and requirements] |               |                    |                  |

### Security Circumstances and Exceptions






