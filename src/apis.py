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
    Plan a trip from {query['origin']} to {query['destination']} from {query['start_date']} to {query['end_date']}. 
    The budget for hotel reservations during this period is {query['budget']}. 
    Please call the flights, stays, and activities agents to obtain the results. 
    Note that this is just for planning, and no booking should be made. """
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
    You have previously formulated a plan for the user. However, the user is not satisfied and has put forward some opinions to you. Please regenerate the plan according to the relevant information.
    ### User's requirement:
    Plan to travel from {query['origin']} to {query['destination']}, with the time period from {query['start_date']} to {query['end_date']}, and the budget for hotel reservation during this period is {query['budget']}.
    ### Old plan:
    {query['plan']}
    ### Modification opinions:
    {query['suggest']}
    Please, according to the actual situation, call one or more of the flgits, stays and activities agents to obtain the result.
    Note 1: Don't forget to return the result in JSON format.
    Note 2: There is no need to call or return information of agents that are not used. 
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
    prompt = f"""You have previously formulated a plan for the user. The user has made some selections regarding the plan. Please call booking_agent to perform the booking operation according to the user's selections.
### Plan:
{query['plan']}
### User's opinion:
{query['suggest']}
Please handle it by calling booking_agent according to the actual situation. Don't forget to return the result in JSON format. 
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