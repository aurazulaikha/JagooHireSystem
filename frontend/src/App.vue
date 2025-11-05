<template>
  <div :class="['wrapper', { 'no-sidebar': $route.meta.noSidebar }]">
      <div
        class="sidebar"
        data-color="white"
        data-active-color="danger"
        v-if="!$route.meta.noSidebar"
      >
      <div class="logo">
        <a class="simple-text logo-mini">
          <div class="logo-image-small">
            <img src="/assets/img/logo.jpg">
          </div>
        </a>
        <a class="simple-text logo-normal">
          JagooHire
   
        </a>
      </div>
      <Sidebar />
    </div>
    <div class="main-panel">
     
      <Nav v-if="!$route.meta.noNavbar"/>
      <router-view />
     
    <Footer v-if="!$route.meta.noNavbar"/>
    </div>
  </div>
</template>

<script>
import Footer from "./components/Footer.vue";
import Nav from "./components/Nav.vue";
import Sidebar from "./components/Sidebar.vue";

export default {
  name: 'App',
  components: {
    Footer, 
    Nav,
    Sidebar,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  /* text-align: center; */
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}

.wrapper.no-sidebar .main-panel {
  margin-left: 0 !important;
  width: 100% !important;
}

.wrapper.no-sidebar {
  display: flex;
}

.wrapper.no-sidebar .sidebar {
  display: none;
  width: 0;
}

</style>