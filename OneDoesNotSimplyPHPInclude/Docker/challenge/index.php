<?php
// make sure to sanitise
function is_allowed($value)
{
    // The users can't be allowed to access the '/flag.txt' file, or do path traversal
    foreach (["..", "flag"] as $term) {
        if (stripos($value, $term) !== false) {
            return false;
        }
    }
    return true;
}

if (isset($_GET["page"])) {
    $file = $_GET["page"];
} else {
    $file = "";
}

if (is_allowed($file) and $file != "") {
    include $file;
} else {
    // Have a default page
    include "home.php";
}

$content = <<<HTML
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Brainf*ck 101</title>
        <meta name="viewport" contents="width=device-width, inital-scale=1.0">
        <link rel="stylesheet" href="style.css">
    </head>
<nav>
    <a href="?page=home.php">Home</a>
    <a href="?page=about.php">About</a>
    <a href="?page=learn.php">Learn</a>
    <a href="?page=contact.php">Contact</a>
</nav>
<h2>Welcome to Brainf*ck 101</h2>
HTML;

$content .= $data;

$content .= <<<HTML
<br>
<footer>
    Happy Brainf*cking!
</footer>
HTML;

echo $content;
?>
