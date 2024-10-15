<template>
    <nav class="navbar">
  <ul><router-link to="/student_details" class="details">Student Details</router-link></ul>
</nav>
    <h1>Private Page Access {{ username }}</h1>
    <button @click="logout">Logout</button>
    
</template>
<script>
export default {
    data(){
        return{
            isAuthenticated:true,
            username:localStorage.getItem('username'),
        }
    },
    
    methods: {
        logout(){
            localStorage.removeItem('username');
            localStorage.removeItem('isAuthenticated');
        this.isAuthenticated =false;
        this.$router.push('/');
        }
    }
}
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
</style>