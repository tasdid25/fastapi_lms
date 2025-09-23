from pydantic_settings import BaseSettings


class Settings(BaseSettings):
	DATABASE_URL: str = "sqlite:///./sms.db"
	APP_ENV: str = "development"
	SCRAPER_USER_AGENT: str = (
		"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
	)

	class Config:
		env_file = ".env"
		env_file_encoding = "utf-8"


def get_settings() -> Settings:
	return Settings()