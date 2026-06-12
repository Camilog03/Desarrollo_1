INSERT INTO mesas (n_mesa, estado) VALUES (1, 'disponible');

INSERT INTO categorias (nombre) VALUES ('Entradas'), ('Platos fuertes'), ('Bebidas'), ('Postres');

INSERT INTO productos (nombre, descripcion, precio, id_categoria) VALUES
('Patacones con hogao', 'Patacones fritos con salsa de tomate y cebolla', 8000, 1),
('Empanadas (3)', 'Empanadas de pipián con ají', 7000, 1),
('Bandeja paisa', 'Frijoles, chicharrón, huevo, arroz, carne molida y aguacate', 28000, 2),
('Sudado de pollo', 'Pollo guisado con papas y yuca', 22000, 2),
('Hamburguesa especial', 'Carne, queso, lechuga, tomate y papas fritas', 20000, 2),
('Limonada natural', 'Limonada con panela o azúcar', 6000, 3),
('Jugo de mora', 'Jugo natural de mora con leche o agua', 6000, 3),
('Agua', 'Agua mineral 500ml', 3000, 3),
('Flan de caramelo', 'Flan casero con caramelo', 9000, 4),
('Arroz con leche', 'Arroz con leche y canela', 7000, 4);
