<template>
  <div class="background-container">
    <div class="login-container">
      <h1 class="text-center">Login</h1>
      <form class="login-form" @submit.prevent="handleLogin">
        <!-- Username -->
        <div class="form-group">
          <label for="username" class="form-label label-bold">Username</label>
          <input type="text" id="username" v-model="username" class="form-control input-large" placeholder="Masukkan username" required/>
        </div>

        <!-- Password -->
        <div class="form-group">
          <label for="password" class="form-label label-bold">Password</label>
          <input type="password" id="password" v-model="password" class="form-control input-large" placeholder="Masukkan password" required/>
        </div>

        <div v-if="error" class="error">{{ error }}</div>

        <!-- Tombol -->
        <button class="btn login-button" type="submit">Login</button>
      </form>
    </div>
  </div>

  </template>

<script>
import axios from "axios";

export default {
  name: "LoginPage",
  data() {
    return {
      username: "",
      password: "",
      error: "",
    };
  },
  methods: {
    async handleLogin() {
      this.error = "";
      try {
        const response = await axios.post(
          "http://localhost:5000/login",
          {
            username: this.username,
            password: this.password,
          },
          { withCredentials: true }
        );

        const { token, user_id, role } = response.data;

        // Simpan token dan user_id untuk akses endpoint protected
        localStorage.setItem("user", JSON.stringify({ token, user_id, role }));
        localStorage.setItem("justLoggedIn", "true");

        // Redirect sesuai role
        if (role === "HCM") this.$router.push("/dashboard");
        else if (role === "AM") this.$router.push("/dashboard");
        else if (role === "Director") this.$router.push("/dashboard");
      } catch (err) {
        this.error = err.response?.data?.message || "Login gagal";
      }
    },
  },
};
</script>

<style scoped>

body,
html {
  margin: 0;
  padding: 0;
  height: 100%;
  width: 100%;
  overflow: auto;
}

.background-container {
  width: 100vw;
  height: 100vh;
  background-image: url("/public/assets/img/bg.jpg");
  background-size: cover;
  background-position: center;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  position: relative;
}

.background-container::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(148, 110, 110, 0.4);
  z-index: 1;
}

.background-container > * {
  position: relative;
  z-index: 2;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.login-button {
  background-color: #946e6e !important;
  color: #fff !important;
  padding: 12px 20px;
  border: none;
  width: fit-content;
  font-size: 14px;
  border-radius: 3px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  align-self: center;
  margin-top: 10px;
}

.login-button:hover {
  background-color: #795858 !important;
}

.login-container {
  max-width: 400px;
  width: 100%;
  padding: 30px;
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}

.card-body {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.label-bold {
  font-weight: bold;
  font-size: 17px;
}

.input-large {
  height: 50px;
  font-size: 1rem;
  padding: 10px;
  width: 100%;
  box-sizing: border-box;
}

.error {
  color: rgb(220, 19, 19);
  margin-top: 10px;
  font-size: 14px;
}

h1 {
  font-weight: bold;
  margin-bottom: 20px;
  font-size: 24px;
  text-align: center;
}

button {
  background-color: #946e6e !important;
  color: #fff !important;
}

.login-container p a {
  color: #946e6e;
  font-weight: bold;
}

.custom-swal-popup {
  font-size: 12px !important;
  padding: 10px !important;
  max-width: 280px !important;
}

.custom-swal-title {
  font-size: 14px !important;
  margin-bottom: 5px !important;
}

.custom-swal-text {
  font-size: 14px !important;
}

.custom-success-icon .swal2-success-line-tip,
.custom-success-icon .swal2-success-line-long,
.custom-success-icon .swal2-success-ring {
  border-color: #946e6e !important;
}

.custom-success-icon .swal2-success-ring {
  border-width: 4px !important;
}

.custom-error-button {
  background-color: #946e6e !important;
  color: #fff !important;
  font-size: 12px !important;
  padding: 5px 15px !important;
  border-radius: 4px !important;
  box-shadow: none !important;
  border: none !important;
}
</style>
