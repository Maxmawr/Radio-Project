<?php
session_start();

// Define the admin credentials
define('ADMIN_USERNAME', 'admin');
define('ADMIN_PASSWORD', 'password123'); // Use a more secure password in practice

// Check if the form was submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Validate the credentials
    if ($username === ADMIN_USERNAME && $password === ADMIN_PASSWORD) {
        // Set session variables
        $_SESSION['loggedin'] = true;
        header('Location: admin.php'); // Redirect to the admin page
        exit();
    } else {
        echo 'Invalid username or password!';
    }
}
?>