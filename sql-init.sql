CREATE TABLE stairs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    step_depth FLOAT,
    step_height FLOAT,
    step_width FLOAT,
    slope_deg FLOAT,
    stair_angle_deg FLOAT,
    pos_x FLOAT,
    pos_y FLOAT,
    sep_dist_parallel FLOAT,
    sep_dist_perpendicular FLOAT,
    anchor_point FLOAT,
    stair_parts INT,
    risers INT,
    treads INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pointclouds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),        -- new field
    frame_number INT,
    data LONGBLOB
);

ALTER TABLE stairs
ADD COLUMN pointcloud_id INT,
ADD CONSTRAINT fk_pointcloud
    FOREIGN KEY (pointcloud_id) REFERENCES pointclouds(id)
    ON DELETE SET NULL
    ON UPDATE CASCADE;


ALTER TABLE `pointcloud`
ADD COLUMN `image_2d` LONGBLOB NULL COMMENT 'Stores 2D image data',
ADD COLUMN `camera_params` JSON NULL COMMENT 'Stores camera parameters in JSON format';

ALTER TABLE pointclouds
    ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Create the gtStaircase table
CREATE TABLE gtStaircase (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    root_name VARCHAR(255),
    type VARCHAR(50),
    width DECIMAL(5,2),
    num_steps INT,
    riser_height DECIMAL(5,3),
    tread_depth DECIMAL(5,3),
    tactile_strips_before_length DECIMAL(5,3),
    tactile_strips_after_length DECIMAL(5,3),
    parapet_height DECIMAL(5,3),
    parapet_max_opening_diameter DECIMAL(5,3),
    handrails_side VARCHAR(50),
    handrails_height DECIMAL(5,3),
    handrails_extension_length DECIMAL(5,3),
    handrails_offset_from_wall DECIMAL(5,3)
);

ALTER TABLE gtStaircase
    ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
