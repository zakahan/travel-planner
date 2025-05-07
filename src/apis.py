import json
import json_repair
from pydantic import BaseModel, Field
from typing import Any
from fastapi import FastAPI, Body
from agents.root_agent import execute
import uvicorn

app = FastAPI()


class BaseResponse(BaseModel):
    code: int = Field(200, description='API status code')
    msg: str = Field('success', description='API message')
    data: Any = Field(None, description='API data')

    class Config:
        json_schema_extra = {
            'example': {
                'code': 200,
                'msg': 'success'
            }
        }

@app.post("/plan")
async def plan(
        query: dict = Body(..., description="plan list"),
) -> BaseResponse:
    prompt = f"""
计划从{query['origin']} 前往{query['destination']}，时间是从{query['start_date']}到{query['end_date']}，
在这期间，预定酒店的预算是{query['budget']}，请调用flights，stays和activities agents来获得结果。注意，不要预定，只是做计划
"""
    results = await execute(prompt)
    results_dict = json_repair.loads(results[0])
    

    return BaseResponse(
        code=200,
        msg="success",
        data=results_dict
    )


@app.post("/replan")
async def replan(
    query: dict = Body(..., description="re-plan"),
) -> BaseResponse:
    prompt = f"""
    你之前给用户制定过计划，但是用户并不满意，并且给你提出了一些意见，请你根据相关信息重新生成计划
    ### 用户的需求：
    计划从{query['origin']} 前往{query['destination']}，时间是从{query['start_date']}到{query['end_date']}，
    在这期间，预定酒店的预算是{query['budget']}
    ### 旧计划：
    {query['plan']}
    ### 修改意见
    {query['suggest']}
    请你根据实际情况，调用flgits，stays和activities agents中的一个或多个来获得结果，
    注意1：别忘了结果要用json的样式返回。
    注意2:不需要调用也不需要返回没有使用的agent的信息
    """
    result = await execute(prompt)
    results_dict = json_repair.loads(result[0])

    return BaseResponse(
        code=200,
        msg="success",
        data=results_dict
    )

@app.post("/booking")
async def booking(
    query: dict = Body(..., description="booking everything."),
) -> BaseResponse:
    prompt = f"""你之前给用户制定过计划，用户对计划做了一些选择，请你根据用户的选择，调用booking_agent来执行预定操作
    ### 计划：
    {query['plan']}
    ### 用户的意见
    {query['suggest']}  
    请你根据实际情况，调用booking_agent进行处理，别忘了结果请用json样式返回
"""
    result = await execute(prompt)
    results_dict = json_repair.loads(result[0])

    return BaseResponse(
        code=200,
        msg="success",
        data=results_dict
    )



if __name__ == "__main__":
    uvicorn.run(
        app="apis:app",
        host="localhost",
        port=8090,
        reload=True
    )