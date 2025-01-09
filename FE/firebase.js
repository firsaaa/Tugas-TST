import { initializeApp } from "https://www.gstatic.com/firebasejs/9.15.0/firebase-app.js";
import { 
    getAuth, 
    GoogleAuthProvider, 
    signInWithPopup
} from "https://www.gstatic.com/firebasejs/9.15.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyAtFMHucKrE4VG3FT-uMJLwjJxf5WRKxPg",
    authDomain: "coworkingspace-tst.firebaseapp.com",
    projectId: "coworkingspace-tst",
    storageBucket: "coworkingspace-tst.appspot.com",
    messagingSenderId: "441126500998",
    appId: "1:441126500998:web:dedbe375624c3fd10eef07"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { auth, googleProvider, signInWithPopup };
