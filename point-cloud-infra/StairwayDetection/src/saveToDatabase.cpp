#include <mysql/mysql.h>
#include <iostream>
#include <string>
#include <cstring>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>

// MySQL version of saveStairsToDatabase
void saveStairsToDatabase(
    const std::string& host,
    unsigned int port,
    const std::string& user,
    const std::string& password,
    const std::string& dbName,
    float step_depth,
    float step_height,
    float step_width,
    float slope_deg,
    float stair_angle_deg,
    int stairParts,
    float distX,
    float distY,
    float distPar,
    float distOrt,
    float anchorPoint,
    int risers,
    int treads,
    int point_cloud_id
) {
    MYSQL* conn = mysql_init(nullptr);
    if (!conn) {
        std::cerr << "mysql_init() failed" << std::endl;
        return;
    }

    if (!mysql_real_connect(conn, host.c_str(), user.c_str(), password.c_str(),
                            dbName.c_str(), port, nullptr, 0)) {
        std::cerr << "Connection failed: " << mysql_error(conn) << std::endl;
        mysql_close(conn);
        return;
    }

    // Prepare insert statement with placeholders
    const char* sql = R"(
        INSERT INTO stairs
        (step_depth, step_height, step_width, slope_deg, stair_angle_deg,
         pos_x, pos_y, sep_dist_parallel, sep_dist_perpendicular, anchor_point,
         stair_parts, risers, treads, pointcloud_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    )";

    MYSQL_STMT* stmt = mysql_stmt_init(conn);
    if (!stmt) {
        std::cerr << "mysql_stmt_init() failed" << std::endl;
        mysql_close(conn);
        return;
    }

    if (mysql_stmt_prepare(stmt, sql, strlen(sql))) {
        std::cerr << "mysql_stmt_prepare() failed: " << mysql_stmt_error(stmt) << std::endl;
        mysql_stmt_close(stmt);
        mysql_close(conn);
        return;
    }

    // Bind parameters
    MYSQL_BIND bind[14];
    memset(bind, 0, sizeof(bind));

    // FLOATs (use MYSQL_TYPE_DOUBLE for C++ float/double)

    double step_depth_d = static_cast<double>(step_depth);
    double step_height_d = static_cast<double>(step_height);
    double step_width_d = static_cast<double>(step_width);
    double slope_deg_d = static_cast<double>(slope_deg);
    double stair_angle_d = static_cast<double>(stair_angle_deg);
    double distX_d = static_cast<double>(distX);
    double distY_d = static_cast<double>(distY);
    double distPar_d = static_cast<double>(distPar);
    double distOrt_d = static_cast<double>(distOrt);
    double anchorPoint_d = static_cast<double>(anchorPoint);
    bind[0].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[0].buffer = &step_depth_d;
    bind[1].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[1].buffer = &step_height_d;
    bind[2].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[2].buffer = &step_width_d;
    bind[3].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[3].buffer = &slope_deg_d;
    bind[4].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[4].buffer = &stair_angle_d;
    bind[5].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[5].buffer = &distX_d;
    bind[6].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[6].buffer = &distY_d;
    bind[7].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[7].buffer = &distPar_d;
    bind[8].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[8].buffer = &distOrt_d;
    bind[9].buffer_type = MYSQL_TYPE_DOUBLE;
    bind[9].buffer = &anchorPoint_d;

    // INTs (use MYSQL_TYPE_LONG for C++ int)
    bind[10].buffer_type = MYSQL_TYPE_LONG;
    bind[10].buffer = (void *)&stairParts;
    bind[11].buffer_type = MYSQL_TYPE_LONG;
    bind[11].buffer = (void *)&risers;
    bind[12].buffer_type = MYSQL_TYPE_LONG;
    bind[12].buffer = (void *)&treads;
    bind[13].buffer_type = MYSQL_TYPE_LONG;
    bind[13].buffer = (void *)&point_cloud_id;



    if (mysql_stmt_bind_param(stmt, bind))
    {
        std::cerr << "mysql_stmt_bind_param() failed: " << mysql_stmt_error(stmt) << std::endl;
        mysql_stmt_close(stmt);
        mysql_close(conn);
        return;
    }

    // Execute statement
    if (mysql_stmt_execute(stmt)) {
        std::cerr << "Insert failed: " << mysql_stmt_error(stmt) << std::endl;
    } else {
        std::cout << "Stairs saved to MySQL database successfully." << std::endl;
    }

    mysql_stmt_close(stmt);
    mysql_close(conn);
}





// Function to fetch point cloud from MySQL and load it into PCL
 pcl::PointCloud<pcl::PointXYZ>::Ptr loadPointCloudFromMySQL(
    const std::string& host,
    unsigned int port,
    const std::string& user,
    const std::string& password,
    const std::string& dbName,
    int id
) {
    MYSQL *conn = mysql_init(nullptr);
    if (!mysql_real_connect(conn, host.c_str(), user.c_str(), password.c_str(),
                            dbName.c_str(), port, nullptr, 0)) {
        throw std::runtime_error("MySQL connection failed: " + std::string(mysql_error(conn)));
    }

    // Prepare query
    std::string query = "SELECT data FROM pointclouds WHERE id=" + std::to_string(id);
    if (mysql_query(conn, query.c_str())) {
        mysql_close(conn);
        throw std::runtime_error("MySQL query failed: " + std::string(mysql_error(conn)));
    }

    MYSQL_RES *res = mysql_store_result(conn);
    if (!res) {
        mysql_close(conn);
        throw std::runtime_error("Failed to store MySQL result: " + std::string(mysql_error(conn)));
    }

    MYSQL_ROW row = mysql_fetch_row(res);
    if (!row || !row[0]) {
        mysql_free_result(res);
        mysql_close(conn);
        throw std::runtime_error("No point cloud found for the given name/frame");
    }

    unsigned long *lengths = mysql_fetch_lengths(res);
    size_t blob_size = lengths[0];
    std::vector<char> buffer(blob_size);
    memcpy(buffer.data(), row[0], blob_size);

    mysql_free_result(res);
    mysql_close(conn);

    // Write blob to temporary file
    std::string temp_filename = "temp_pointcloud.pcd";
    std::ofstream outfile(temp_filename, std::ios::binary);
    outfile.write(buffer.data(), blob_size);
    outfile.close();

    // Load into PCL PointCloud
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(new  pcl::PointCloud<pcl::PointXYZ>);
    if (pcl::io::loadPCDFile(temp_filename, *cloud) == -1) {
        throw std::runtime_error("Failed to load PCD file into PCL");
    }

    return cloud;
}