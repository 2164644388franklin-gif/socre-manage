from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import math

app = FastAPI()

# 配置跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 数据存储 ==========

# 课表数据存储
list_schedule = [
    {"course_id": 1, "course_name": "语文", "day_of_week": 1, "period": 1, "teacher": "王老师", "classroom": "101"},
    {"course_id": 2, "course_name": "数学", "day_of_week": 1, "period": 2, "teacher": "李老师", "classroom": "202"},
    {"course_id": 3, "course_name": "英语", "day_of_week": 1, "period": 3, "teacher": "张老师", "classroom": "303"},
    {"course_id": 4, "course_name": "物理", "day_of_week": 2, "period": 1, "teacher": "赵老师", "classroom": "实验室A"},
    {"course_id": 5, "course_name": "化学", "day_of_week": 2, "period": 2, "teacher": "陈老师", "classroom": "实验室B"},
    {"course_id": 6, "course_name": "体育", "day_of_week": 3, "period": 4, "teacher": "刘老师", "classroom": "操场"},
    {"course_id": 7, "course_name": "历史", "day_of_week": 4, "period": 1, "teacher": "孙老师", "classroom": "105"},
    {"course_id": 8, "course_name": "信息技术", "day_of_week": 5, "period": 3, "teacher": "周老师", "classroom": "机房1"},
]

list_user = [
    {"user_id": 1, "username": "Mary", "score": 99},
    {"user_id": 2, "username": "Lisa", "score": 96},
    {"user_id": 3, "username": "Mask", "score": 95},
    {"user_id": 4, "username": "Altman", "score": 85},
    {"user_id": 5, "username": "Dario", "score": 72},
    {"user_id": 6, "username": "Tom", "score": 58},
    {"user_id": 7, "username": "Jerry", "score": 45},
    {"user_id": 8, "username": "Alice", "score": 88},
    {"user_id": 9, "username": "Bob", "score": 67},
    {"user_id": 10, "username": "Charlie", "score": 91},
    {"user_id": 11, "username": "David", "score": 60},
    {"user_id": 12, "username": "Eve", "score": 76},
]


def get_grade(score: int) -> str:
    """根据分数返回等级"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 60:
        return "C"
    else:
        return "D"


def user_to_item(user: dict) -> dict:
    """将用户字典转为带 grade 的响应"""
    return {
        "user_id": user["user_id"],
        "username": user["username"],
        "score": user["score"],
        "grade": get_grade(user["score"]),
    }


# ========== Pydantic 模型 ==========
class Item(BaseModel):
    user_id: int
    username: str
    score: int
    grade: str = ""


class UsersResponse(BaseModel):
    items: List[Item]
    total: int
    page: int
    page_size: int
    total_pages: int


class StatsResponse(BaseModel):
    total: int
    average_score: float
    max_score: int
    min_score: int
    grade_distribution: dict


class UpdateUser(BaseModel):
    score: int


# ========== 课表模型 ==========
class CourseItem(BaseModel):
    course_id: int
    course_name: str
    day_of_week: int
    period: int
    teacher: str
    classroom: str


class CreateCourse(BaseModel):
    course_name: str
    day_of_week: int
    period: int
    teacher: str
    classroom: str


class UpdateCourse(BaseModel):
    course_name: Optional[str] = None
    day_of_week: Optional[int] = None
    period: Optional[int] = None
    teacher: Optional[str] = None
    classroom: Optional[str] = None


# ========== 课表 API 接口 ==========

@app.get("/schedule", response_model=List[CourseItem])
def get_schedule(
    day_of_week: Optional[int] = Query(None, description="按星期筛选: 1周一 ~ 5周五"),
):
    """获取完整课表，可按星期筛选"""
    if day_of_week is not None:
        return [c for c in list_schedule if c["day_of_week"] == day_of_week]
    return list_schedule


@app.post("/schedule", response_model=CourseItem)
def add_course(course: CreateCourse):
    """添加课程到课表，同一星期+节次不能重复"""
    # 检查是否已存在相同位置课程
    for c in list_schedule:
        if c["day_of_week"] == course.day_of_week and c["period"] == course.period:
            raise HTTPException(status_code=409, detail=f"周{course.day_of_week} 第{course.period}节已有课程，请先删除再添加")
    new_id = max([c["course_id"] for c in list_schedule]) + 1 if list_schedule else 1
    new_course = {
        "course_id": new_id,
        "course_name": course.course_name,
        "day_of_week": course.day_of_week,
        "period": course.period,
        "teacher": course.teacher,
        "classroom": course.classroom,
    }
    list_schedule.append(new_course)
    return new_course


@app.put("/schedule/{course_id}", response_model=CourseItem)
def update_course(course_id: int, course: UpdateCourse):
    """修改课程信息"""
    for c in list_schedule:
        if c["course_id"] == course_id:
            new_day = course.day_of_week if course.day_of_week is not None else c["day_of_week"]
            new_period = course.period if course.period is not None else c["period"]
            # 检查新位置是否与其他课程冲突
            for other in list_schedule:
                if other["course_id"] != course_id and other["day_of_week"] == new_day and other["period"] == new_period:
                    raise HTTPException(
                        status_code=409,
                        detail=f"周{new_day} 第{new_period}节已有课程，请先删除再添加",
                    )
            if course.course_name is not None:
                c["course_name"] = course.course_name
            c["day_of_week"] = new_day
            c["period"] = new_period
            if course.teacher is not None:
                c["teacher"] = course.teacher
            if course.classroom is not None:
                c["classroom"] = course.classroom
            return c
    raise HTTPException(status_code=404, detail="课程不存在")


@app.delete("/schedule/{course_id}")
def delete_course(course_id: int):
    """删除课程"""
    for i, c in enumerate(list_schedule):
        if c["course_id"] == course_id:
            del list_schedule[i]
            return {"message": "课程删除成功"}
    raise HTTPException(status_code=404, detail="课程不存在")


# ========== API 接口 ==========


@app.get("/")
def root():
    return FileResponse("index.html")


@app.get("/user/{user_id}", response_model=Item)
def get_user(user_id: int):
    for user in list_user:
        if user["user_id"] == user_id:
            return user_to_item(user)
    raise HTTPException(status_code=404, detail="用户不存在")


@app.get("/users", response_model=UsersResponse)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="按用户名模糊搜索"),
    min_score: Optional[int] = Query(None, description="最低分筛选"),
    max_score: Optional[int] = Query(None, description="最高分筛选"),
    sort_by: Optional[str] = Query(None, description="排序字段: user_id / username / score"),
    sort_order: Optional[str] = Query("asc", description="排序方向: asc / desc"),
):
    # 1. 筛选
    filtered = list_user.copy()

    if keyword:
        filtered = [u for u in filtered if keyword.lower() in u["username"].lower()]

    if min_score is not None:
        filtered = [u for u in filtered if u["score"] >= min_score]

    if max_score is not None:
        filtered = [u for u in filtered if u["score"] <= max_score]

    # 2. 排序
    if sort_by in ("user_id", "username", "score"):
        reverse = sort_order == "desc"
        filtered.sort(key=lambda u: u[sort_by], reverse=reverse)

    # 3. 分页
    total = len(filtered)
    total_pages = max(1, math.ceil(total / page_size))

    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]

    return UsersResponse(
        items=[user_to_item(u) for u in paginated],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/users/stats", response_model=StatsResponse)
def get_users_stats():
    """获取成绩统计数据"""
    if not list_user:
        return StatsResponse(
            total=0,
            average_score=0.0,
            max_score=0,
            min_score=0,
            grade_distribution={"A": 0, "B": 0, "C": 0, "D": 0},
        )

    scores = [u["score"] for u in list_user]
    total = len(scores)
    avg = round(sum(scores) / total, 2)

    distribution = {"A": 0, "B": 0, "C": 0, "D": 0}
    for u in list_user:
        distribution[get_grade(u["score"])] += 1

    return StatsResponse(
        total=total,
        average_score=avg,
        max_score=max(scores),
        min_score=min(scores),
        grade_distribution=distribution,
    )


@app.post("/register", response_model=Item)
def usr_register(user: Item):
    new_user_id = max([u["user_id"] for u in list_user]) + 1 if list_user else 1
    new_user = {
        "user_id": new_user_id,
        "username": user.username,
        "score": user.score,
    }
    list_user.append(new_user)
    return user_to_item(new_user)


@app.delete("/user/{user_id}")
def delete_user(user_id: int):
    for index, existing_user in enumerate(list_user):
        if existing_user["user_id"] == user_id:
            del list_user[index]
            return {"message": "用户删除成功"}
    raise HTTPException(status_code=404, detail="用户信息不存在")


@app.put("/user/{user_id}", response_model=Item)
def update_user(user_id: int, user: UpdateUser):
    for existing_user in list_user:
        if existing_user["user_id"] == user_id:
            existing_user["score"] = user.score
            return user_to_item(existing_user)
    raise HTTPException(status_code=404, detail="用户不存在")