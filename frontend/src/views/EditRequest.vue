<template>
  <div class="edit-request-wrapper">
    <div class="edit-request-container">
      <h1 class="page-title">Edit Request</h1>
      <div class="title-underline"></div>

      <form @submit.prevent="updateRequest">
        <label>Role</label>
        <input v-model="form.role" required />

        <label>Nama Perusahaan</label>
        <input v-model="form.company_name" required />

        <label>Durasi</label>
        <input v-model="form.duration" required />

        <label>Jumlah</label>
        <input v-model.number="form.quantity" type="number" required />

        <label>Gaji Maksimal</label>
        <input v-model.number="form.max_salary" type="number" />

        <label>Lokasi</label>
        <input v-model="form.location" />

        <label>Metode Kerja</label>
        <select v-model="form.work_method" required>
          <option v-for="method in workMethods" :key="method" :value="method">
            {{ method.charAt(0).toUpperCase() + method.slice(1) }}
          </option>
        </select>

        <label>Jadwal Kerja</label>
        <input v-model="form.work_schedule" />

        <label>Estimasi Tanggal Mulai</label>
        <input v-model="form.est_start_date" type="date" />

        <label>Level</label>
        <select v-model="form.level" required>
          <option v-for="lvl in levels" :key="lvl" :value="lvl">{{ lvl }}</option>
        </select>

        <label>Current Stage</label>
        <select v-model="form.current_stage" required>
          <option v-for="stage in stages" :key="stage" :value="stage">{{ stage }}</option>
        </select>

        <label>Deskripsi Pekerjaan</label>
        <textarea v-model="form.job_description"></textarea>

        <div class="form-actions">
          <button type="submit">Simpan Perubahan</button>
          <button type="button" @click="goBack">Batal</button>
        </div>
      </form>

      <!-- ALERT -->
      <div v-if="showAlert" :class="['alert-box', alertType]">
        <p>{{ alertMessage }}</p>
        <button @click="closeAlert">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "EditRequest",
  data() {
    const user = JSON.parse(localStorage.getItem("user")) || {};
    return {
      form: {
        id: null,
        role: "",
        company_name: "",
        duration: "",
        quantity: 1,
        max_salary: null,
        location: "",
        work_method: "onsite",
        work_schedule: "",
        est_start_date: "",
        level: "Junior",
        current_stage: "New Request",
        job_description: "",
      },
      workMethods: ["onsite", "hybrid", "remote"],
      levels: ["Junior", "Middle", "Senior"],
      stages: ["New Request","Aptitude","Technical","Professional","Trial","Onboarding","Finish"],
      token: user.token || "",
      showAlert: false,
      alertMessage: "",
      alertType: "",
      alertCallback: null,
    };
  },
  mounted() {
    this.loadRequest();
  },
  methods: {
    async loadRequest() {
      const requestId = this.$route.params.id;
      try {
        const res = await axios.get("http://localhost:5000/requests", {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        const req = res.data.find((r) => r.id == requestId);
        if (req) {
          if (req.est_start_date) {
            req.est_start_date = new Date(req.est_start_date)
              .toISOString()
              .substr(0, 10);
          }

          this.form = {
            id: req.id,
            role: req.role || "",
            company_name: req.company_name || "",
            duration: req.duration || "",
            quantity: req.quantity || 1,
            max_salary: req.max_salary || null,
            location: req.location || "",
            work_method:
              this.workMethods.find(
                (m) => m.toLowerCase() === (req.work_method || "").toLowerCase()
              ) || "onsite",
            work_schedule: req.work_schedule || "",
            est_start_date: req.est_start_date || "",
            level:
              this.levels.find(
                (l) => l.toLowerCase() === (req.level || "").toLowerCase()
              ) || "Junior",
            current_stage:
              this.stages.find((s) => s === (req.current_stage || "")) ||
              "New Request",
            job_description: req.job_description || "",
          };
        } else {
          this.showCustomAlert("Request tidak ditemukan.", "error");
        }
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal memuat data request.", "error");
      }
    },
    async updateRequest() {
      try {
        await axios.put(
          `http://localhost:5000/requests/${this.form.id}`,
          { ...this.form },
          { headers: { Authorization: `Bearer ${this.token}` } }
        );
        this.showCustomAlert("Request berhasil diperbarui!", "success", () => {
          this.goBack();
        });
      } catch (err) {
        console.error(err);
        this.showCustomAlert("Gagal memperbarui request.", "error");
      }
    },
    goBack() {
      this.$router.push("/requests");
    },
    showCustomAlert(message, type = "success", callback = null) {
      this.alertMessage = message;
      this.alertType = type;
      this.showAlert = true;
      this.alertCallback = callback;
    },
    closeAlert() {
      this.showAlert = false;
      if (this.alertCallback) this.alertCallback();
    },
  },
};
</script>

<style scoped>
.edit-request-wrapper {
  display: flex;
  justify-content: flex-start;
  padding: 100px 0 0 50px;
  min-height: 100vh;
  background: linear-gradient(180deg, #f9f3f3, #fff);
}

.edit-request-container {
  width: 450px;
  background: #fff;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  gap: 15px;
}

/* Header */
.page-title {
  font-size: 28px;
  color: #7a3e3e;
  font-weight: 700;
}
.title-underline {
  width: 80px;
  height: 4px;
  background: #a26060;
  border-radius: 5px;
  margin-bottom: 15px;
}

/* Form */
form label {
  display: block;
  margin-top: 10px;
  font-weight: 500;
}
form input,
form select,
form textarea {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
  margin-top: 5px;
}

/* Form actions */
.form-actions {
  margin-top: 15px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.form-actions button {
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}
.form-actions button[type="submit"] {
  background: #43a032;
  color: white;
}
.form-actions button[type="button"] {
  background: #ccc;
  color: #333;
}

/* Alert */
.alert-box {
  margin-top: 15px;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  font-weight: 500;
}
.alert-box.success {
  background: #d1e7dd;
  color: #0f5132;
}
.alert-box.error {
  background: #f8d7da;
  color: #842029;
}
.alert-box button {
  margin-top: 10px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  background: #333;
  color: #fff;
}
</style>
