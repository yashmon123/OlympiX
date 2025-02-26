import os
from groq import Groq

class OlympicsInsightBot:
    def __init__(self):
        self.client = Groq(
            api_key=os.environ["GROQ_API_KEY"]
        )
        
    def get_insights(self, data_context):
        prompt = f"""
        As an Olympics data analyst, provide insights about the following Olympic data:
        {data_context}
        
        Please provide:
        1. Key observations
        2. Notable trends
        3. Interesting facts
        
        Keep the response concise and informative.
        """
        
        completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=500
        )
        
        return completion.choices[0].message.content

    def get_component_insights(self, data_context):
        prompt = f"""
        As an Olympics data analyst, analyze this data and provide key insights:
        {data_context}
        
        Please provide:
        1. Key Findings
        2. Notable Patterns
        3. Recommendations or Interesting Facts
        
        Keep the response concise and focused on the most important points.
        """
        
        completion = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt,
            }],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=300
        )
        
        return completion.choices[0].message.content
