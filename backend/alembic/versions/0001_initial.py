from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("organizations", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(150), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(500), nullable=False), sa.Column("role", sa.String(30), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)), sa.UniqueConstraint("organization_id", "email", name="uq_user_org_email"))
    op.create_index("ix_users_organization_id", "users", ["organization_id"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("jobs", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("required_skills", sa.Text(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_index("ix_jobs_organization_id", "jobs", ["organization_id"])
    op.create_table("candidates", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("phone", sa.String(80), nullable=False), sa.Column("resume_path", sa.String(500)), sa.Column("resume_text", sa.Text(), nullable=False), sa.Column("score", sa.Float()), sa.Column("created_at", sa.DateTime(timezone=True)))
    op.create_index("ix_candidates_organization_id", "candidates", ["organization_id"])
    op.create_index("ix_candidates_email", "candidates", ["email"])


def downgrade():
    op.drop_index("ix_candidates_email", table_name="candidates")
    op.drop_index("ix_candidates_organization_id", table_name="candidates")
    op.drop_table("candidates")
    op.drop_index("ix_jobs_organization_id", table_name="jobs")
    op.drop_table("jobs")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_organization_id", table_name="users")
    op.drop_table("users")
    op.drop_table("organizations")
