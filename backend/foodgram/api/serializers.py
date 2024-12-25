import uuid
from rest_framework import exceptions, serializers
from django.core.validators import RegexValidator, validate_email
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from drf_extra_fields.fields import Base64ImageField
User = get_user_model()

MAX_LENGTH = 150
EMAIL_MAX_LENGTH = 254

class UserRequiredFieldsSerializerMixin(serializers.ModelSerializer):
    """Миксин для сериалайзеров с использованием модели юзера."""

    username = serializers.CharField(
        max_length=MAX_LENGTH,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=('Поле может содержать буквы, '
                     'цифры, и символы: @/./+/-/_ .')
        )]
    )
    email = serializers.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        validators=[validate_email],
        required=True
    )


class TokenObtainByCodeSerializer(serializers.ModelSerializer):
    """Кастомный сериалайзер для получения токена."""

    username = serializers.CharField()
    email = serializers.EmailField()


    class Meta:
        model = User
        fields = ['username', 'email']


    def validate(self, data):
        username = data.get("username")
        user_object = User.objects.filter(
            username=username
        ).first()
        if user_object is None:
            raise exceptions.NotFound(
                "Пользователь не найден."
            )
        return data

    def create(self, validated_data):
        # Создаем токен для пользователя.
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            'auth_token': str(refresh.access_token),
        }
    

class UserProfileSerializer(
    UserRequiredFieldsSerializerMixin,
    serializers.ModelSerializer
):
    """Сериалайзер для работы с запросами к страницам пользователей."""

    first_name = serializers.CharField(max_length=MAX_LENGTH, required=True)
    last_name = serializers.CharField(max_length=MAX_LENGTH, required=True)
    password = serializers.CharField(max_length=MAX_LENGTH, required=True)
    avatar = serializers.ImageField(required=False)
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'last_name',
            'first_name',
            'password',
            'email',
            'avatar',
        ]


    def validate(self, data):

        view = self.context['view']
        obj_pk = view.kwargs.get('pk')
        if obj_pk:
            # при запросе отдельной страницы
            if obj_pk == 'me':
                user_object = User.objects.get(id=self.id)
            else:
                user_object = User.objects.get(id=obj_pk)
            return user_object
        # при создании нового пользователя
        username = data.get('username')
        user_email = data.get('email')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                'username': [
                    ('Логин уже занят.')
                ]
            })
        if User.objects.filter(email=user_email).exists():
            raise serializers.ValidationError({
                'email': ['Введнный адрес уже занят.']
            })
        return data

    def create(self, validated_data):
        user_object = User.objects.create_user(**validated_data)
        return user_object

   
    def to_representation(self, instance):
        """Исключить поле 'password' из ответа."""

        representation = super().to_representation(instance)
        representation.pop('password', None)
        return representation
    

class ChangeProfilePasswordSerializer(serializers.ModelSerializer):
    """Смена пароля профиля."""

    new_password = serializers.CharField(max_length=MAX_LENGTH, required=True)
    current_password = serializers.CharField(max_length=MAX_LENGTH, required=True)

    class Meta:
        model = User
        fields = [
            'password',
        ]

    def validate(self, data):
        current_pass = data.get("current_password")
        new_pass = data.get("new_password")
        if new_pass == current_pass:
            raise serializers.ValidationError({
                'new_password': ['Новый пароль не может быть равен старому.',],
            })
        return data

    def create(self, validated_data):
        User.objects.update(
            id=self.id,
            password=validated_data['new_password']
        )
        return super().create(validated_data)


class ProfleAvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер работы с аватарами пользователей."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = [
            'avatar',
        ]

    # def update(self, validated_data):
    #     User.objects.update(id=self.id, avatar=validated_data["avatar"])
    #     return validated_data

    
    # def perform_destroy(self, instance):
    #     User.objects.update(id=self.id, avatar=None)
