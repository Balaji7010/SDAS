// Import the necessary Firebase modules
import { initializeApp } from "https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/9.0.0/firebase-auth.js";

// Your web app's Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyBKw_vl8UfCICaV7Jk2jFRlGVuz6FBq-vY",
    authDomain: "smart-735ee.firebaseapp.com",
    projectId: "smart-735ee",
    storageBucket: "smart-735ee.appspot.com",
    messagingSenderId: "740869532483",
    appId: "1:740869532483:web:0177463afb3454df59ddf6",
    measurementId: "G-23KTM0WD59"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Get the login form and add a submit event listener
const loginForm = document.getElementById('loginForm');
loginForm.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    // Clear previous error messages
    document.getElementById('emailError').innerText = '';
    document.getElementById('passwordError').innerText = '';

    signInWithEmailAndPassword(auth, email, password)
        .then((userCredential) => {
            // Successful login
            const user = userCredential.user;
            console.log('User logged in:', user);
            // Redirect or show success message
            window.location.href = 'http://127.0.0.1:5000'; // Replace with your dashboard URL
        })
        .catch((error) => {
            const errorCode = error.code;
            const errorMessage = error.message;
            console.error('Error during login:', errorCode, errorMessage);

            // Display error message based on error code
            if (errorCode === 'auth/wrong-password') {
                alert('Incorrect password. Please try again.'); // Alert message for incorrect password
                document.getElementById('passwordError').innerText = 'Incorrect password. Please try again.';
            } else if (errorCode === 'auth/user-not-found') {
                alert('No user found with this email.'); // Alert message for user not found
                document.getElementById('emailError').innerText = 'No user found with this email.';
            } else if (errorCode === 'auth/invalid-email') {
                alert('Invalid email format.'); // Alert message for invalid email
                document.getElementById('emailError').innerText = 'Invalid email format.';
            } else {
                alert(errorMessage); // Alert message for general error
                document.getElementById('emailError').innerText = errorMessage; // Display general error
            }
        });
});

// Google Sign-In
const googleSignInBtn = document.getElementById('googleSignInBtn');
googleSignInBtn.addEventListener('click', () => {
    const provider = new GoogleAuthProvider();
    
    signInWithPopup(auth, provider)
        .then((result) => {
            // The signed-in user info.
            const user = result.user;

            // Check if the user's email ends with your allowed domain
            const allowedDomain = "dhanushpanchacharam@gmail.com"; // Replace with your domain

            if (user.email.endsWith(allowedDomain)) {
                console.log('User signed in with Google:', user);
                // Redirect or show success message
                window.location.href = 'http://127.0.0.1:5000'; // Replace with your dashboard URL
            } else {
                // If the email domain is not allowed, sign the user out
                auth.signOut().then(() => {
                    alert("You are not authorized to use this application.");
                    console.log('User signed out due to unauthorized domain:', user.email);
                });
            }
        })
        .catch((error) => {
            // Handle Errors here.
            const errorCode = error.code;
            const errorMessage = error.message;
            console.error('Error during Google sign-in:', errorCode, errorMessage);
            alert(errorMessage); // Alert for Google sign-in errors
        });
});
