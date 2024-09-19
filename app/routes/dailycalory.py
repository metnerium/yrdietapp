from fastapi import APIRouter, Depends, HTTPException
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
    if height <= 0 or weight <= 0:
        raise ValueError("Height and weight must be positive numbers.")
    bmi = weight / ((height / 100) ** 2)
    return round(bmi, 2)


def calculate_bmr(height: float, weight: float, age: int, gender: str) -> float:
    """
    Расчет базального метаболизма (BMR) по формуле Харриса-Бенедикта.
    """
    if not all([height, weight, age, gender]):
        raise ValueError("All parameters (height, weight, age, gender) must be provided.")

    if not isinstance(gender, str):
        raise ValueError("Gender must be a string.")

    gender = gender.lower()
    if gender == "male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    elif gender == "female":
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    else:
        raise ValueError("Invalid gender. Must be 'male' or 'female'.")
    return round(bmr, 2)


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
    if not activity_level:
        raise ValueError("Activity level must be provided.")

    activity_level = activity_level.lower()
    if activity_level not in activity_factor:
        raise ValueError(
            "Invalid activity level. Must be one of: 'sedentary', 'lightly active', 'moderately active', 'very active', 'extra active'.")
    daily_calorie_intake = bmr * activity_factor[activity_level]
    return round(daily_calorie_intake, 2)


@router.get("/bmi")
async def get_bmi(current_user: User = Depends(get_current_user_dependency)):
    try:
        if not current_user.height or not current_user.weight:
            return {"bmi": 0, "message": "Height or weight not provided."}
        bmi = calculate_bmi(float(current_user.height), float(current_user.weight))
        return {"bmi": bmi}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/daily-calorie-intake")
async def get_daily_calorie_intake(current_user: User = Depends(get_current_user_dependency)):
    try:
        if not all([current_user.height, current_user.weight, current_user.age, current_user.gender,
                    current_user.activity_level]):
            return {"daily_calorie_intake": 0, "message": "Some required user data is missing."}

        bmr = calculate_bmr(float(current_user.height), float(current_user.weight), int(current_user.age),
                            current_user.gender)
        daily_calorie_intake = calculate_daily_calorie_intake(bmr, current_user.activity_level)
        return {"daily_calorie_intake": daily_calorie_intake}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))