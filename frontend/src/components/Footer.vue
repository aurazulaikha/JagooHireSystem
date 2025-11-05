<!-- eslint-disable vue/multi-word-component-names -->

<template>
  <footer class="custom-footer">
    <div class="container-fluid">
      <div class="footer-left">
        <nav class="footer-nav"></nav>
      </div>
      <div class="footer-right">
        <span class="copyright">© 2025</span>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.custom-footer {
  background: linear-gradient(180deg, #ffffff, #ffffff); /* senada dengan dashboard-wrapper */
  border-top: 1px solid #f1e4e4;
  color: #7a3e3e;
  padding: 20px 40px;
  font-family: "Poppins", sans-serif;
  font-size: 14px;
}

.container-fluid {
  display: flex;
  justify-content: space-between; /* kiri dan kanan */
  align-items: center;
}

.footer-right {
  text-align: right;
}

.footer-left {
  text-align: left;
}

.copyright {
  font-weight: 500;
}
</style>
