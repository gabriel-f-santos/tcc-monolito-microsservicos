module "network" {
  source       = "./modules/network"
  project_name = var.project_name
  my_ip        = var.my_ip
}

module "iam" {
  source       = "./modules/iam"
  project_name = var.project_name
}

module "database" {
  source       = "./modules/database"
  project_name = var.project_name
  db_password  = var.db_password

  vpc_id             = module.network.vpc_id
  private_subnet_ids = module.network.private_subnet_ids
  ec2_sg_id          = module.network.ec2_sg_id
}

module "compute" {
  source       = "./modules/compute"
  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  vpc_id            = module.network.vpc_id
  public_subnet_ids = module.network.public_subnet_ids
  alb_sg_id         = module.network.alb_sg_id
  ec2_sg_id         = module.network.ec2_sg_id
  instance_profile  = module.iam.instance_profile_name
  ecr_repo_url      = module.iam.ecr_repo_url
  database_url      = module.database.connection_url
}
