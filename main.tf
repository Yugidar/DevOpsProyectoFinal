provider "aws" {
  region = "us-east-1"
}


#Creacion VPC
resource "aws_vpc" "vpc_PF" {
  cidr_block = "10.10.0.0/20"
  tags= {
    Name = "VPC_ProyectoFinal"
  }
}

#Creacion de la subnet

#Subnet Publica
resource "aws_subnet" "subnet_publica_PF" {
  vpc_id                  = aws_vpc.vpc_PF.id
  cidr_block              = "10.10.0.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "SubnetPublicaProyectoFinal"
  }
}

#Subnet Privada
resource "aws_subnet" "subnet_privada_PF" {
  vpc_id                  = aws_vpc.vpc_PF.id
  cidr_block              = "10.10.1.0/24"
  map_public_ip_on_launch = true
  tags = {
    Name = "SubnetPrivadaProyectoFinal"
  }
}

#Creacion del gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc_PF.id

  tags = {
    Name = "GW_AP"
  }
}

#Tabla de Rutas
resource "aws_route_table" "rutas_PF" {
  vpc_id = aws_vpc.vpc_PF.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags ={
    Name = "Rutas_publicas"
  }
}

#Asociacion de las tablas

#Publica
resource "aws_route_table_association" "asociacion_PF_Publica" {
  subnet_id      = aws_subnet.subnet_publica_PF.id
  route_table_id = aws_route_table.rutas_PF.id
}

#Privada
resource "aws_route_table_association" "asociacion_PF_Privada" {
  subnet_id      = aws_subnet.subnet_privada_PF.id
  route_table_id = aws_route_table.rutas_PF.id
}


#GRUPOS DE SEGURIDAD

#Grupo de Seguridad para el Windows Jump Server
resource "aws_security_group" "windows_js_sg" {
  name        = "Grupo de seguridad para el jump server del proyecto"
  description = "Entrada de RDP y Salida de SSH"
  vpc_id      = aws_vpc.vpc_PF.id

  #Trafico RDP
  ingress {
    from_port   = 3389
    to_port     = 3389
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #Trafico SSH

  egress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#Grupo de Seguridad para linux Web Server Front End
resource "aws_security_group" "linux_ws_front_sg" {
  name        = "Grupo de seguridad para el web server frontend del proyecto"
  description = "Entrada de SSH y Salida de HTTP"
  vpc_id      = aws_vpc.vpc_PF.id

  #Trafico SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #Trafico HTTP

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

#Grupo de Seguridad para linux Web Server Back End
resource "aws_security_group" "linux_ws_back_sg" {
  name        = "Grupo de seguridad para el web server backend del proyecto"
  description = "Entrada de SSH y Salida de SSH"
  vpc_id      = aws_vpc.vpc_PF.id

  #Trafico SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

}


#Instancias

#Instancia Windows Jump Server

resource "aws_instance" "Instancia_Windows_JumpServer" {
  ami           = "ami-0c798d4b81e585f36"
  instance_type = "t2.medium"
  subnet_id     = aws_subnet.subnet_publica_PF.id

  vpc_security_group_ids = [aws_security_group.windows_js_sg.id]
  key_name = "vockey"

  associate_public_ip_address = true

  tags = {
    Name = "Instancia Windows Jump Server"
  }
}

#Instancia Web Linux Front End 

resource "aws_instance" "Instancia_Linux_WebServer_Frontend" {
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.subnet_publica_PF.id

  vpc_security_group_ids = [aws_security_group.linux_ws_front_sg.id]
  key_name = "vockey"

  associate_public_ip_address = true

  tags = {
    Name = "Instancia Linux Servidor Web Frontend"
  }
}

#Instancias Web Windows Back End
resource "aws_instance" "Instancia_Linux_WebServer_Backend" {
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.micro"
  subnet_id     = aws_subnet.subnet_privada_PF.id

  vpc_security_group_ids = [aws_security_group.linux_ws_back_sg.id]
  key_name = "vockey"

  associate_public_ip_address = true

  tags = {
    Name = "Instancia Linux Servidor Web Frontend"
  }
}

#Outputs
#JumpServer
output "Ip_Servidor" {
  description = "ip publica del jump server"
  value = aws_instance.Instancia_Windows_JumpServer.public_ip
}

#FrontEnd
output "Ip_Servidor" {
  description = "ip publica del frontend"
  value = aws_instance.Instancia_Linux_WebServer_Frontend.public_ip
}

#Backend 
output "Ip_Servidor" {
  description = "ip publica del backend"
  value = aws_instance.Instancia_Linux_WebServer_Backend.public_ip
}

