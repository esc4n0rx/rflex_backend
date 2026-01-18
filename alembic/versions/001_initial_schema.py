"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-16

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Cria tabela admin_users
    op.create_table(
        'admin_users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_superadmin', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        comment='Usuários administradores do sistema'
    )
    op.create_index('ix_admin_users_email', 'admin_users', ['email'])

    # Cria tabela companies
    op.create_table(
        'companies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('trading_name', sa.String(255), nullable=False),
        sa.Column('legal_name', sa.String(255), nullable=False),
        sa.Column('cnpj', sa.String(20), unique=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20)),
        sa.Column('address', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        comment='Empresas clientes'
    )
    op.create_index('ix_companies_cnpj', 'companies', ['cnpj'])

    # Cria tabela plans
    op.create_table(
        'plans',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('max_devices', sa.Integer(), nullable=False),
        sa.Column('price_per_device', sa.Float(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('features', sa.Text()),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_enterprise', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        comment='Planos de licenciamento'
    )

    # Cria tabela licenses
    op.create_table(
        'licenses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('code', sa.String(32), nullable=False, unique=True),
        sa.Column('company_id', sa.String(36), sa.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plan_id', sa.String(36), sa.ForeignKey('plans.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, default='inactive'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        comment='Licenças de uso'
    )
    op.create_index('ix_licenses_code', 'licenses', ['code'])

    # Cria tabela device_activations
    op.create_table(
        'device_activations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('license_id', sa.String(36), sa.ForeignKey('licenses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('device_id', sa.String(36), nullable=False, unique=True),
        sa.Column('device_name', sa.String(255)),
        sa.Column('device_manufacturer', sa.String(100)),
        sa.Column('device_model', sa.String(100)),
        sa.Column('android_version', sa.String(20)),
        sa.Column('app_version', sa.String(20)),
        sa.Column('hardware_info', sa.JSON()),
        sa.Column('activated_at', sa.DateTime(), nullable=False),
        sa.Column('last_validated_at', sa.DateTime()),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, default=False),
        sa.Column('revoked_at', sa.DateTime()),
        sa.Column('revoke_reason', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        comment='Ativações de dispositivos'
    )
    op.create_index('ix_device_activations_device_id', 'device_activations', ['device_id'])

    # Cria tabela validation_logs
    op.create_table(
        'validation_logs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('device_activation_id', sa.String(36), sa.ForeignKey('device_activations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('is_offline', sa.Boolean(), nullable=False, default=False),
        sa.Column('error_message', sa.Text()),
        sa.Column('validated_at', sa.DateTime(), nullable=False),
        sa.Column('response_time_ms', sa.String(20)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        comment='Logs de validação de licença'
    )


def downgrade() -> None:
    op.drop_table('validation_logs')
    op.drop_table('device_activations')
    op.drop_table('licenses')
    op.drop_table('plans')
    op.drop_table('companies')
    op.drop_table('admin_users')
