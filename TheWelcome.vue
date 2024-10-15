<template>
<nav class="navbar">
  <ul><router-link to="/student_admission" class="admission">Admission</router-link></ul>
</nav>
<div class="container">
    <h1 class="heading">Welcome</h1>
  <button
      type="button"
      class="btn"
      @click="showModal"
    >
      Login
    </button>
  </div>

    <!--<TheWelcome v-show="isModalVisible" @close="closeModal"/>-->
  
  <transition name="modal-fade">
  <div class="modal-backdrop" v-if="isModalVisible">
    <div class="modal">
      <header class="modal-header">
        <slot name="header">Login</slot>
        <button type="button" class="btn-close" @click="closeModal">X</button>
      </header>

      <section class="modal-body">
        <slot name="body">
          <form @submit.prevent="submitForm">
            <div class="input-div">
              <div class="div-label"><label class="label">Register number</label></div>
            <input v-model="regnum" class="form-inputs" type="text">
            <p v-if="regnum.length < 6 && regnum.length!=0" class="message">Register number should have atleast 6 characters</p>
            </div>
            <div class="input-div">
              <div class="div-label"><label class="label">Password</label></div>
            <input v-model="password" class="form-inputs" required type="password">
            </div>
            <div>
              
            </div>
            
          </form>
        </slot>
       </section>

      <footer class="modal-footer">
        <!--<slot name="footer" v-if="fetchapi.length>0">
          authenticated
        </slot>-->
        <div class="btn-container"><button class="btn-submit" @click="submitForm" type="submit">Submit</button>
        <button type="button" class="btn-green" @click="closeModal">
          Close
        </button></div>
      </footer>
    </div>
  </div>
  </transition>
  
</template>

<script>
  export default {
    data() {
      return {
        isModalVisible: false,
        regnum: '',
        password: '',
        fetchapi: ''
      };
    },
    methods: {
      close() {
        this.$emit('close');
      },
      showModal() {
        this.isModalVisible = true;
      },
      closeModal() {
        this.isModalVisible = false;
      },
      submitForm(){
        console.log(this.regnum);
        fetch(`http://127.0.0.1:8000/login/${this.regnum}/${this.password}`)
        .then((res) => res.json())
        .then((data) => {this.fetchapi = data.access_token;
          if(this.fetchapi){
          localStorage.setItem('isAuthenticated',true);
          localStorage.setItem('username',data.username)
          this.$router.push('/student_private');
        }
        })
        .catch((err) => console.log(err.message));
      }
    },
  };
</script>

<style>
.navbar{
  background-color: #badbd5;
  position: fixed;
  top:0;
  left:0;
  width: 100%;
  height: 46px;
}
ul{
  float:left;
  padding-left: 30px;
  font-size: 30px;
  list-style-type: none;
  justify-content: space-around;
}
a:hover{
  border-radius: 2px;
}
.btn{
  padding:20px;
  font-size: larger;
  background-color: #4AAE9B;
  border-radius: 5px;
  width: max-content;
  
}
.heading{
  padding: 15px;
  font-size: 100px;
  color:#4AAE9B;
}
.container{
  justify-content: space-evenly;
}
  .modal-backdrop {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: rgba(0, 0, 0, 0.3);
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .modal {
    background: #FFFFFF;
    box-shadow: 2px 2px 20px 1px;
    width: 30%;
    display: flex;
    flex-direction: column;
    border-radius: 5px;
  }

  .modal-header,
  .modal-footer {
    padding: 40px;
    display: flex;
  }
  .btn-container{
    display: flex;
    justify-content: space-evenly;
  }
  .btn-submit{
    padding: 10px;
    width: 30%;
    background-color: #4AAE9B;
    color: white;
    border: 1px solid #4AAE9B;
    border-radius: 10px;
    font-size: 20px;
  }
  .message{
    color: rgb(223, 71, 71);
  }
  .btn-green {
    color: white;
    background: #4AAE9B;
    border: 1px solid #4AAE9B;
    border-radius: 10px;
    width: 30%;
    font-size: 20px;
  }
  .form-inputs{
    width: 80%;
    padding: 8px;
    font-size: large;
  }
  .label{
    font-size: large;
    font-weight: 400;
  }
  .input-div{
    padding-bottom: 20px;
    padding-left: 15%;
  }
  .body{
    justify-content: center;
  }
  .modal-header {
    position: relative;
    border-bottom: 1px solid #eeeeee;
    color: #4AAE9B;
    justify-content: center;
    font-size: 50px;
    font-weight: bold;
  }
  
  .modal-footer {
    border-top: 1px solid #eeeeee;
    flex-direction: column;
    justify-content: flex-end;
  }
  .div-label{
    padding-bottom: 10px;
  }
  .modal-body {
    position: relative;
    padding: 50px 20px;
  }

  .btn-close {
    position: absolute;
    top: 0;
    right: 0;
    border: none;
    font-size: 20px;
    padding: 10px;
    cursor: pointer;
    font-weight: bold;
    color: #4AAE9B;
    background: transparent;
  }

  
  .modal-fade-enter,
  .modal-fade-leave-to {
    opacity: 0;
  }

  .modal-fade-enter-active,
  .modal-fade-leave-active {
    transition: opacity .3s ease;
  }
</style>