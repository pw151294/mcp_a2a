import logging
from typing import Optional, AsyncGenerator

from app.domain.models.event import Event, MessageEvent, PlanEvent, PlanEventStatus
from app.domain.models.message import Message
from app.domain.models.plan import Plan, Step
from app.domain.services.agents.base import BaseAgent
from app.domain.services.prompts import PLANNER_SYSTEM_PROMPT, SYSTEM_PROMPT, CREATE_PLAN_PROMPT, UPDATE_PLAN_PROMPT

logger = logging.getLogger(__name__)

"""
多Agent系统 = PlannerAgent + ReActAgent

顺序：
1. PlannerAgent生成规划
2. 循环取出规划中的子步骤，让ReActAgent执行，依次迭代
3. ReActAgent执行完每一个子步骤之后，需要将子步骤结果+Plan传递给PlannerAgent让其更新计划/Plan
4. 循环取出规划中的子步骤，让ReActAgent执行，依次迭代
5. 。。。。。。
6. 直到所有的任务/子步骤都完成，这时候将子步骤的所有结果汇总进行总结（ReActAgent）

PlannerAgent：
- 功能将用户的需求拆解成多个子任务 + 根据已完成的子任务更新规划
- 提示词：创建规划的prompt，更新规划的prompt

ReActAgent：
- 功能： 迭代执行完每一个任务， 汇总所有的子任务进行总结
- 提示词：执行任务的prompt，汇总总结prompt
"""


class PlanAgent(BaseAgent):
    """规划Agent 将用户的任务/需求拆解成多个子步骤"""
    name: str = "PlannerAgent"
    _system_prompt: str = SYSTEM_PROMPT + PLANNER_SYSTEM_PROMPT
    _format: Optional[str] = "json_object"
    _tool_choice: Optional[str] = None

    async def create_plan(self, message: Message) -> AsyncGenerator[Event, None]:
        """根据用户传递的消息创建计划/规划 迭代返回对应的事件"""
        # 根据用户传递的消息生成Plan的提示词
        query = CREATE_PLAN_PROMPT.format(
            message=message.message,
            attachments="\n".join(message.attachments)
        )

        # 调用invoke函数返回迭代事件
        async for event in self.invoke(query):
            # 规划智能体因为使用json_object，正常情况不会返回MessageEvent
            if isinstance(event, MessageEvent):
                # 记录日志并使用json解析器解析得到对应的数据
                logger.info(f"规划智能体生成消息：{event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                # 将解析对象转换成Plan计划
                plan = Plan.model_validate(parsed_obj)

                # 返回Plan事件表示规划创建成功
                yield PlanEvent(plan=plan, status=PlanEventStatus.CREATED)
            else:
                yield event

    async def update_plan(self, plan: Plan, step: Step) -> AsyncGenerator[Event, None]:
        """根据传递的原始规划+子步骤更新事件"""
        query = UPDATE_PLAN_PROMPT.format(
            plan=plan.model_dump_json(),
            step=step.model_dump_json()
        )

        # 调用invoke获取对应的事件
        async for event in self.invoke(query):
            # 判断规划Agent生成的事件是不是消息事件
            if isinstance(event, MessageEvent):
                # 记录日志并解析json
                logger.info(f"规划智能体生成消息：{event.message}")
                parsed_obj = await self._json_parser.invoke(event.message)

                # 将解析对象转换成Plan
                updated_plan = Plan.model_validate(parsed_obj)

                # 拷贝更新中的计划列表
                new_steps = [Step.model_validate(step) for step in step.steps]

                # 查询旧计划第一个未完成的计划
                first_pending_idx = None
                for idx, step in enumerate(plan.steps):
                    if not step.done:
                        first_pending_idx = idx
                        break

                # 判断是否存在未完成的步骤 如果有则执行更新
                if first_pending_idx is not None:
                    # 获取历史已完成的子步骤并更新
                    updated_steps = plan.steps[:first_pending_idx]
                    updated_steps.extend(new_steps)

                    # 更新plan规划
                    plan.steps = updated_steps

                # 返回规划更新事件
                yield PlanEvent(plan=updated_plan, status=PlanEventStatus.UPDATED)

            else:
                yield event
