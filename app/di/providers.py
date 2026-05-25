from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import AsyncSessionLocal
from app.config import settings

from app.repositories.user_repo import UserRepository
from app.repositories.post_repo import PostRepository
from app.repositories.group_repo import GroupRepository
from app.repositories.comment_repo import CommentRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.repositories.post_image_repo import PostImageRepository
from app.repositories.comment_image_repo import CommentImageRepository

from app.services.jwt_service import JWTService

from app.use_cases.auth_use_case import AuthUseCase
from app.use_cases.refresh_token_use_case import RefreshTokenUseCase
from app.use_cases.post_use_case import PostUseCase
from app.use_cases.group_use_case import GroupUseCase
from app.use_cases.comment_use_case import CommentUseCase


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_settings(self) -> settings.__class__:
        return settings


class ServiceProvider(Provider):
    @provide(scope=Scope.APP)
    def jwt_service(self, s: settings.__class__) -> JWTService:
        return JWTService(s)


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterable[AsyncSession]: 
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


class RepositoryProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repo(self, s: AsyncSession) -> UserRepository:
        return UserRepository(s)

    @provide(scope=Scope.REQUEST)
    def post_repo(self, s: AsyncSession) -> PostRepository:
        return PostRepository(s)

    @provide(scope=Scope.REQUEST)
    def group_repo(self, s: AsyncSession) -> GroupRepository:
        return GroupRepository(s)

    @provide(scope=Scope.REQUEST)
    def comment_repo(self, s: AsyncSession) -> CommentRepository:
        return CommentRepository(s)

    @provide(scope=Scope.REQUEST)
    def refresh_repo(self, s: AsyncSession) -> RefreshTokenRepository:
        return RefreshTokenRepository(s)

    @provide(scope=Scope.REQUEST)
    def post_image_repo(self, s: AsyncSession) -> PostImageRepository:
        return PostImageRepository(s)

    @provide(scope=Scope.REQUEST)
    def comment_image_repo(self, s: AsyncSession) -> CommentImageRepository:
        return CommentImageRepository(s)


class UseCaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def auth_uc(self, user_repo: UserRepository) -> AuthUseCase:
        return AuthUseCase(user_repo)

    @provide(scope=Scope.REQUEST)
    def refresh_uc(
        self,
        refresh_repo: RefreshTokenRepository,
        user_repo: UserRepository,
        jwt_service: JWTService,
    ) -> RefreshTokenUseCase:
        return RefreshTokenUseCase(refresh_repo, user_repo, jwt_service)

    @provide(scope=Scope.REQUEST)
    def post_uc(
        self,
        post_repo: PostRepository,
        group_repo: GroupRepository,
        post_image_repo: PostImageRepository,
    ) -> PostUseCase:
        return PostUseCase(post_repo, group_repo, post_image_repo)

    @provide(scope=Scope.REQUEST)
    def group_uc(self, group_repo: GroupRepository) -> GroupUseCase:
        return GroupUseCase(group_repo)

    @provide(scope=Scope.REQUEST)
    def comment_uc(
        self,
        comment_repo: CommentRepository,
        post_repo: PostRepository,
        comment_image_repo: CommentImageRepository,
    ) -> CommentUseCase:
        return CommentUseCase(comment_repo, post_repo, comment_image_repo)


all_providers = [
    ConfigProvider(),
    ServiceProvider(),
    DatabaseProvider(),
    RepositoryProvider(),
    UseCaseProvider(),
]
