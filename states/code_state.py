from aiogram.dispatcher.filters.state import State, StatesGroup


class PublicationState(StatesGroup):
    text = State()


class EstateState(StatesGroup):
    word = State()


class SwearState(StatesGroup):
    word = State()


class ManagerState(StatesGroup):
    username = State()
