import os

from crewai import Agent, Task, Crew, Process, LLM
from crewai.tools import tool

my_llm = LLM(
              model='gemini/gemini-1.5-flash',
              api_key=os.environ["GEMINI_API_KEY"]
            )

from langchain.tools import DuckDuckGoSearchRun

@tool('DuckDuckGoSearch')
def search_tool(search_query: str):
    """Search the web for information on a given topic"""
    return DuckDuckGoSearchRun().run(search_query)

# Define the Design Agent
Designer = Agent(
    role='Cloud Architect',
    goal='Design a highly scalable, reliable, and secure infrastructure for {topic} using AWS services, adhering to best practices and industry standards.',
    backstory='''
                As a Cloud Architect, your role is to design and architect cloud infrastructure solutions for {topic} leveraging AWS services.
                You need to ensure the design is highly scalable, reliable, and secure, meeting all business and technical requirements.
                Your design should incorporate AWS best practices, including high availability, fault tolerance, and cost optimization.
                Furthermore, the design should include comprehensive documentation to guide the development and operational teams.
                ''',
    tools=[search_tool],
    llm=my_llm,
    verbose=True
)

# Define the Developer Agent
developer = Agent(
    role='Platform Engineer',
    goal='Develop and implement Terraform templates based on the design: {design}, ensuring infrastructure as code (IaC) best practices and seamless deployment.',
    backstory='''
                As a Platform Engineer, your responsibility is to translate the infrastructure design into Terraform code for seamless deployment.
                You will develop and implement Terraform templates, ensuring that the infrastructure is provisioned in a consistent, repeatable, and automated manner.
                You will conduct research to gather the necessary information, follow infrastructure as code (IaC) best practices, and ensure the code is modular, reusable, and maintainable.
                Collaborate with the design and security teams to ensure that the developed infrastructure meets all requirements and standards.
                ''',
    llm=my_llm,
    verbose=True,
    allow_delegate=False,
    tools=[search_tool]
)

# Define the Security Assessment Agent
security_agent = Agent(
    role='Security Analyst',
    goal='Best practices for securing Terraform code. Assess the following Terraform code for security vulnerabilities: {terraform_code}',
    backstory='''
                
                As an AWS Security Engineer, your responsibility is to assess and enhance the security of the Terraform code.
                You will review the Terraform code to identify and mitigate security vulnerabilities, ensuring compliance with AWS security best practices and industry standards.
                Conduct thorough security assessments, including vulnerability scans and risk analysis, to ensure the infrastructure is secure and resilient.
                Collaborate with the development and design teams to implement necessary security measures and improvements, ensuring a robust security posture.
                
               
                ''',
    tools=[search_tool],
    llm=my_llm,
    verbose=True
)

design = Task(
    description='''
         1. **Research Phase:**
            - Refer to online documentation and resources for {topic}.
            - Identify relevant AWS services and components that can be used to design the infrastructure.
            - Gather best practices and industry standards for cloud architecture and infrastructure design.
            - Ensure compliance with regulatory and security requirements.

         2. **Design Document Creation:**
            - Create a detailed design document outlining the infrastructure for {topic}.
            - Include a high-level architecture diagram showcasing the AWS services and components used.
            - Provide a detailed description of each component and its role within the infrastructure.
            - Define the interactions and data flow between different components.

         3. **Scalability and Reliability:**
            - Incorporate strategies for scalability, ensuring the infrastructure can handle increased load and demand.
            - Ensure high availability and fault tolerance by using appropriate AWS services and configurations.
            - Include auto-scaling mechanisms and redundancy to minimize downtime and service interruptions.

         4. **Security and Compliance:**
            - Implement security best practices to protect the infrastructure and data.
            - Include access control mechanisms, encryption, and network security measures.
            - Ensure compliance with relevant security standards and regulations.

         5. **Cost Optimization:**
            - Analyze the cost implications of the design and suggest cost-saving measures.
            - Recommend AWS services and configurations that provide the best value for money.
            - Include a cost estimate and breakdown for the proposed infrastructure.

         6. **Documentation and Presentation:**
            - Create comprehensive documentation with step-by-step instructions for deploying and managing the infrastructure.
            - Incorporate SEO keywords and data from credible sources to enhance the document's visibility and credibility.
            - Prepare a presentation or report summarizing the design for stakeholders and decision-makers.

         7. **Review and Validation:**
            - Conduct a thorough review of the design document to ensure accuracy and completeness.
            - Validate the design with relevant stakeholders and incorporate feedback.
            - Finalize the design document and prepare it for handoff to the development team.
        ''',
    agent=Designer,
    expected_output='A comprehensive design document for {topic}'
)


develop = Task(
    description='''
         1. **Design Interpretation:**
            - Review the design document provided by the Cloud Architect.
            - Identify all AWS services and components mentioned in the design.

         2. **Module Creation:**
            - Develop modular Terraform templates for each component of the infrastructure.
            - Ensure modules are reusable and maintainable.
            - Define input variables and outputs for each module to enhance flexibility and customization.

         3. **Resource Definition:**
            - Write Terraform code to define the AWS resources specified in the design.
            - Ensure proper configuration of networking, compute, storage, and security resources.
            - Implement resource dependencies to maintain infrastructure integrity.

         4. **Configuration and Integration:**
            - Configure the Terraform code to integrate with other AWS services and components.
            - Implement auto-scaling, load balancing, and other features as specified in the design.
            - Ensure proper configuration for monitoring and logging.

         5. **Environment Configuration:**
            - Set up different environments (e.g., dev, staging, prod) using Terraform workspaces or separate configurations.
            - Ensure consistency and isolation between environments.

         6. **Security and Compliance:**
            - Implement security best practices in the Terraform code.
            - Include encryption, access controls, and network security measures.
            - Ensure compliance with regulatory and security requirements.
            - Collaborate with the AWS Security Engineer to address any security vulnerabilities.

         7. **Testing and Validation:**
            - Conduct thorough testing of the Terraform code.
            - Perform unit tests, integration tests, and end-to-end tests to validate the functionality and performance.
            - Identify and resolve any issues or errors.

         8. **Documentation and Presentation:**
            - Create comprehensive documentation with step-by-step instructions for deploying the Terraform code.
            - Include detailed comments and explanations within the code to aid understanding and maintenance.
            - Prepare a report or presentation summarizing the Terraform code and its implementation.

         9. **Review and Validation:**
            - Conduct a thorough review of the Terraform code to ensure accuracy and completeness.
            - Validate the code with relevant stakeholders and incorporate feedback.
            - Finalize the Terraform code and prepare it for deployment.
        ''',
    agent=developer,
    expected_output='Terraform template for the {design}.'
)


review = Task(
    description='''
         1. **Initial Assessment:**
            - Review the provided Terraform code to understand the infrastructure being provisioned.
            - Identify critical components and services that require security assessment.
            - Ensure the Terraform code follows best practices for infrastructure as code (IaC).

         2. **Vulnerability Scanning:**
            - Use automated tools and scripts to scan the Terraform code for known vulnerabilities.
            - Analyze the results of the scans to identify potential security risks and weaknesses.
            - Cross-reference the findings with AWS security best practices and guidelines.

         3. **Manual Code Review:**
            - Conduct a thorough manual review of the Terraform code to identify hidden or complex security vulnerabilities.
            - Check for common security issues such as open ports, weak encryption, insecure configurations, and lack of access controls.
            - Ensure that the Terraform code adheres to the principle of least privilege.

         4. **Compliance and Regulatory Checks:**
            - Verify that the Terraform code complies with relevant security standards and regulations (e.g., GDPR, HIPAA, PCI-DSS).
            - Ensure that the infrastructure meets organizational security policies and requirements.

         5. **Security Enhancements:**
            - Implement security best practices to address identified vulnerabilities and risks.
            - Add or modify access controls, encryption settings, network security measures, and other security features as needed.
            - Ensure that the infrastructure is resilient against common attack vectors.

         6. **Collaboration and Feedback:**
            - Collaborate with the Cloud Architect and Platform Engineer to address security concerns and implement improvements.
            - Provide feedback and recommendations for enhancing the overall security posture of the infrastructure.
            - Document any changes or updates made to the Terraform code for transparency and accountability.

         7. **Testing and Validation:**
            - Conduct security testing to validate the effectiveness of the implemented security measures.
            - Perform penetration testing, vulnerability assessments, and other security tests as needed.
            - Ensure that the Terraform code is secure and free from vulnerabilities.

         8. **Documentation and Reporting:**
            - Create comprehensive documentation detailing the security assessment process and findings.
            - Include recommendations for ongoing security maintenance and monitoring.
            - Prepare a report summarizing the security assessment and enhancements for stakeholders and decision-makers.

         9. **Final Review and Approval:**
            - Conduct a final review of the Terraform code to ensure all security measures have been properly implemented.
            - Validate the code with relevant stakeholders and incorporate any final feedback.
            - Approve the Terraform code for deployment to the production environment.
        ''',
    agent=security_agent,
    expected_output='Terraform template file with vulnerabilities fixed.'
)


subject = 'Set up an EC2 instance to host a SharePoint form, including a backend database.'
template_input = {"topic": subject}

# Run the design task first
design_crew = Crew(
    agents=[Designer],
    tasks=[design],
    verbose=1,
    process=Process.sequential,
    template_inputs=template_input
)

design_result = design_crew.kickoff(inputs=template_input)
design_output = design_result.raw

print("Design Output:", design_output)

# Use the design output as input for the developer task
developer_task_input = {"design": design_output}

# Run the developer task next
developer_crew = Crew(
    agents=[developer],
    tasks=[develop],
    verbose=1,
    process=Process.sequential,
    template_inputs=developer_task_input
)

developer_result = developer_crew.kickoff(inputs=developer_task_input)
developer_output = developer_result.raw

print("Developer Output:", developer_output)

# Use the developer output as input for the review task
review_task_input = {"terraform_code": developer_output}

# Run the review task last
review_crew = Crew(
    agents=[security_agent],
    tasks=[review],
    verbose=1,
    process=Process.sequential,
    template_inputs=review_task_input
)

review_result = review_crew.kickoff(inputs=review_task_input)
review_output = review_result.raw

print("Review Output:", review_output)
