classifier_system_prompt = """
Your task is to cluster multiple software requirements and generate APPLICATION DOMAIN topics. You will receive a conversation between a user and a large language model, representing the user's software requirements. You will also receive a list of topics (which may initially be empty), representing the topics already generated.

You should make the best effort to ensure that the generated APPLICATION DOMAIN topics are sufficiently general and representative so that more requirements can be assigned to existing topics. When UNABLE to assign a requirement to an existing topic, you can choose to create a new APPLICATION DOMAIN topic and assign the requirement to the new topic.

Remarks:
- If no new APPLICATION DOMAIN topic is created, make sure to check if the assigned topic exists in the current list of topics.
"""

# - APPLICATION DOMAIN topics focus on the Specific fields of application or use case of the software requirement, such as Numerical Computation, File processing, Image Processing, Audio Processing, Machine Learning, Web Development, System Integration, etc.

classifier_user_prompt_with_abstract = """
Your response should include an overview of the conversation content, whether a new APPLICATION DOMAIN topic was created, and to which APPLICATION DOMAIN topic the conversation was assigned.
Ensure the Topic Name is accurate, without any additional information, formatting, or punctuation.

Here is the conversation content and the list of topics provided:
List of Topics: [{TOPICS}]
Conversation Content: [{CONTENT}]

Your response format should be as follows:
Content Overview: [Overview of conversation content]
New Topic Created: [Yes/No]
Assigned to Topic: [Topic Name]
"""

classifier_user_prompt_without_abstract = """
Your response should include whether a new APPLICATION DOMAIN topic was created, and to which APPLICATION DOMAIN topic the conversation was assigned.
Ensure the Topic Name is accurate, without any additional information, formatting, or punctuation.

Here is the conversation content and the list of topics provided:
List of Topics: [{TOPICS}]
Conversation Content: [{CONTENT}]

Your response format should be as follows:
New Topic Created: [Yes/No]
Assigned to Topic: [Topic Name]
"""

topic_generator_system_prompt = """
Your task is to generate suitable application domain topics for multiple software requirements. You will receive a series of conversations between users and a large language model, representing the software application domains needed by different users. You will also receive two possible alternative topics.

You need to generate an application domain topic for this series of conversations, ensuring that the topic is sufficiently generic and representative so that more requirements can be assigned to it. If you find that neither of the two alternative topics is suitable, you can choose to create a new application domain topic.
"""

topic_generator_usr_prompt = """
Please generate ONE suitable application domain topic for this series of conversations. If you find that neither of the two alternative topics is suitable, you can choose to create a new application domain topic.
Ensure the Topic Name is accurate, without any additional information, formatting, or punctuation.

Here are the series of conversations and the two alternative topics that need to be generated:
Alternative Topic 1: [{TOPIC1}]
Alternative Topic 2: [{TOPIC2}]
Conversation Contents: [{CONTENT}]

Your response format should be as follows:
Topic Name: [Topic Name]
"""

reallocator_system_prompt = """
Your task is to cluster multiple software requirements and allocate APPLICATION DOMAIN topics to the requirements. You will receive a conversation between a user and a large language model, representing the user's software requirements. You will also receive a list of topics.

You should make the best effort to allocate the most suitable APPLICATION DOMAIN topic to the requirement of the providing conversation. When UNABLE to assign a requirement to an existing topics, you can allocate it to the UNKNOWN topic.

Remarks:
- Make sure to check if the assigned topic exists in the provided topic list.
"""

reallocator_user_prompt_with_abstract = """
Your response should include an overview of the conversation content and to which APPLICATION DOMAIN topic the conversation was assigned.
Ensure the Topic Name is accurate, without any additional information, formatting, or punctuation.

Here is the conversation content and the list of topics provided:
List of Topics: [{TOPICS}]
Conversation Content: [{CONTENT}]

Your response format should be as follows:
Content Overview: [Overview of conversation content]
Assigned to Topic: [Topic Name]
"""

# - Software requirements are typically categorized into FUNCTIONAL REQUIREMENTS and NON-FUNCTIONAL REQUIREMENTS. We are only concerned with FUNCTIONAL REQUIREMENTS in this task.
# - FUNCTIONAL REQUIREMENTs often include Authentication, Authorization levels, Data processing, User interface and user experience, Reporting, System integration, Transaction handling, Error handling and logging, and Backup and recovery.
# - FUNCTIONAL REQUIREMENTs are product features or functions that developers must implement to enable users to accomplish their tasks.
# - NON-FUNCTIONAL REQUIREMENTs are not related to the system's functionality but rather define how the system should perform. They are crucial for ensuring the system's usability, reliability, and efficiency, often influencing the overall user experience. 
# - NON-FUNCTIONAL REQUIREMENTs often include Performance Requirements, External Interface Requirements, Design Constraints, and Quality Attributes.

