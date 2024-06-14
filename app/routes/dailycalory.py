from fastapi import APIRouter, Depends
from app.models.user import User
from app.dependencies import get_current_user_dependency

router = APIRouter()

def calculate_bmi(height: float, weight: float) -> float:
    """
    Вычисляет индекс массы тела (ИМТ) на основе веса и роста человека.

    :param weight: Вес человека в килограммах (кг).
    :param height: Рост человека в метрах (м).
    :return: Значение ИМТ, округленное до двух знаков после запятой.
    """
    bmi = weight / ((height/100) ** 2)
    return round(bmi,2)

def calculate_bmr(height: float, weight: float, age: int, gender: str) -> float:
    """
    Расчет базального метаболизма (BMR) по формуле Харриса-Бенедикта.
    """
    if gender.lower() == "male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    elif gender.lower() == "female":
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    else:
        raise ValueError("Invalid gender. Must be 'male' or 'female'.")
    return bmr

def calculate_daily_calorie_intake(bmr: float, activity_level: str) -> float:
    """
    Расчет дневной нормы потребления калорий на основе BMR и уровня активности.
    """
    activity_factor = {
        "sedentary": 1.2,
        "lightly active": 1.375,
        "moderately active": 1.55,
        "very active": 1.725,
        "extra active": 1.9
    }
    if activity_level.lower() not in activity_factor:
        raise ValueError("Invalid activity level. Must be one of: 'sedentary', 'lightly active', 'moderately active', 'very active', 'extra active'.")
    daily_calorie_intake = bmr * activity_factor[activity_level.lower()]
    return daily_calorie_intake

@router.get("/bmi")
async def get_bmi(current_user: User = Depends(get_current_user_dependency)):
    bmi = calculate_bmi(current_user.height, current_user.weight)
    return {"bmi": bmi}

@router.get("/daily-calorie-intake")
async def get_daily_calorie_intake(current_user: User = Depends(get_current_user_dependency)):
    bmr = calculate_bmr(current_user.height, current_user.weight, current_user.age, current_user.gender)
    daily_calorie_intake = calculate_daily_calorie_intake(bmr, current_user.activity_level)
    return {"daily_calorie_intake": daily_calorie_intake}