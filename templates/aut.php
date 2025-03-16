<?php
session_start();

// DB connection setup (optional)
// $conn = new mysqli('localhost', 'root', '', 'login_system');

// if ($conn->connect_error) {
//     die("Connection failed: " . $conn->connect_error);
// }

$valid_username = 'admin';  // Replace with DB check for real-world app
$valid_password = password_hash('password123', PASSWORD_DEFAULT);  // Example password hash

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $username = trim($_POST['username']);
    $password = trim($_POST['password']);

    // Check if fields are empty
    if (empty($username) || empty($password)) {
        echo "Please enter username and password.";
        exit;
    }

    // Fetch user from the database (for real-world use)
    // $sql = "SELECT * FROM users WHERE username=?";
    // $stmt = $conn->prepare($sql);
    // $stmt->bind_param('s', $username);
    // $stmt->execute();
    // $result = $stmt->get_result();
    // if ($result->num_rows == 1) {
    //     $user = $result->fetch_assoc();
    //     $hash_password = $user['password'];
    // }

    // For simplicity, using hardcoded validation
    if ($username === $valid_username && password_verify($password, $valid_password)) {
        $_SESSION['username'] = $username;
        
        // Check for "Remember Me"
        if (isset($_POST['rememberMe'])) {
            setcookie('username', $username, time() + (86400 * 30), "/");  // Set for 30 days
        }

        header('Location: dashboard.php');
        exit;
    } else {
        echo "Invalid username or password.";
    }
}
?>
