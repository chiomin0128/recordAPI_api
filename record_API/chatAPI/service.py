    # chatbot/services.py
import os
import environ
import asyncio

from pinecone import Pinecone

from langchain.prompts import ChatPromptTemplate
from django.utils import timezone



from langchain_core.documents import Document

from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from chatAPI.models import UserSetting, ChatHistory
from chatAPI.serializers import ChatHistorySerializer

env = environ.Env(DEBUG=(bool, True)) 

environ.Env.read_env(
    env_file=os.path.join('recordAPI', '.env')
)

pc = Pinecone(
    api_key=os.environ.get("PINECONE_API_KEY"),   
) 

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


class ChatService:

    @staticmethod
    def manage_user_setting(user_id, settings=None):
        if settings is None:
            # 조회
            try:
                return UserSetting.objects.get(user_id=user_id)
            except UserSetting.DoesNotExist:
                raise ValueError('User setting does not exist')
        else:
            #저장
            user_setting, created = UserSetting.objects.get_or_create(user_id=user_id)
            for key, value in settings.items():
                setattr(user_setting, key, value)
            user_setting.save()
            return user_setting
        

    @staticmethod
    def save_questions_to_vectordb(user_id, data):
        # 벡터 데이터베이스에 저장할 벡터로 변환
        loader = data  # 이미 딕셔너리 형태이므로 변환할 필요 없음
        documents = []

        for idx, category in enumerate(loader['categories']):
            count = 1;
            combined_text = f"Category: {category['category']}"
            for question in category['questions']:
                combined_text += f"{count}. Question: {question['question']}"
                combined_text += f"{count}. Answer: {question['user']}"
                count += 1
            document = Document(
                page_content=combined_text,
                metadata={'user_id': user_id, 'category': category['category']}
            )
            documents.append(document)

        vectorstore_db = PineconeVectorStore.from_documents(
            documents=documents,
            embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY),
            index_name=PINECONE_INDEX_NAME,
            namespace=f"user_{user_id}"
        )

        return {"success": True}

    @staticmethod
    def bot_maker(user_setting):
        # user_id = user_setting.get("user_id")   # 유저 아이디
        # user_log = user_setting.get("user_log") # 유저 DB 만들기 True/False
        # role = user_setting.get('role')         # 역할
        # tone = user_setting.get('tone')         # 스타일
        # goal = user_setting.get('goal')         # 사용자 목표 
        # length = user_setting.get('length')     # 채팅길이
        # topics = user_setting.get('topics')     # 주제 
        # mbti = user_setting.get('MBTI')         # MBTI
        # pers = user_setting.get('pers')         # 성격

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system",
                        f"""역할:   {user_setting.role}\n 
                        대화 스타일: {user_setting.tone}\n   
                        목표:       {user_setting.goal}\n
                        응답 길이:   {user_setting.length}\n
                        주제:       {user_setting.topics}\n\n
                        MBTI:      {user_setting.mbti}\n
                        성격:       {user_setting.pers}
                        위 정보는 당신의 정보입니다.
                        """
                        + "대화기록 참조 : {context}"
                ),
                ("user", "{message}")                
            ]
        )
        return prompt
    
    @staticmethod
    def generate_response(user_id, user_message):
        user_setting = UserSetting.objects.get(user_id=user_id)
        prompt_template = ChatService.bot_maker(user_setting)
        
        

        vectorstore = PineconeVectorStore(
            index_name=PINECONE_INDEX_NAME,
            namespace=f"user_{user_id}",
            embedding=OpenAIEmbeddings(api_key=OPENAI_API_KEY)
        )
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0,
            api_key=OPENAI_API_KEY,
        )
        retriever = vectorstore.as_retriever()


        ragchain = (
            {"context": retriever, "message": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )

        
        
        response = ragchain.invoke(user_message)
        ChatHistory.objects.create(user_id=user_id,type=False,  message=response,created_at=timezone.now())
        ChatHistory.objects.create(user_id=user_id,type=True,  message=user_message,created_at=timezone.now())
        return response
    

    @staticmethod
    def chathistory(user_id):
        user_settings = ChatHistory.objects.filter(user_id=user_id)
        serializer = ChatHistorySerializer(user_settings, many=True)
        return serializer.data