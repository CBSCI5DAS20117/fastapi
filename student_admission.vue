<template>
    <div class="form">
        <form @submit.prevent="submitForm">
            <div class="form-row">
            <div class="form-element">
                <div><label class="form-label">Name</label></div>
                <div><input type="text" class="form-input" v-model="name"></div>
            </div>
            <div class="form-element">
                <div><label class="form-label">Date of Birth</label></div>
                <div><input type="date" class="form-input" v-model="dob"></div>
            </div>
            </div>
            <div class="form-row">
            <div class="form-element">
                <div><label class="form-label">Qualification</label></div>
                <div><input type="text" class="form-input" v-model="qualification"></div>
            </div>
            <div class="form-element">
                <div><label class="form-label">Address</label></div>
                <div><input type="text" class="form-input" v-model="address"></div>
            </div>
            </div>
            <div class="form-row">
            <div class="form-element">
                <div><label class="form-label">University</label></div>
                <select class="form-input" v-model="select_uni" @change="listColleges">
                    <option v-for="university in universities" :key="university">
                        {{ university }}
                    </option>
                </select>
            </div>
            <div class="form-element">
                <div><label class="form-label">College</label></div>
                <select class="form-input" v-model="select_college" @change="listCourses">
                    <option v-if="select_uni.length===0">Select University first</option>
                    <option v-for="college in colleges" :key="college">
                        {{ college }}
                    </option>
                </select>
            </div>
            </div>
            <div class="form-course-row">
            <div class="form-element">
                <div><label class="form-label">Course</label></div>
                <select class="form-input" v-model="select_course">
                    <option v-if="select_college.length===0">Select College first</option>
                    <option v-if="courses.length===0">No courses available</option>
                    <option v-for="course in courses" :key="course">
                        {{ course }}
                    </option>
                </select>
            </div>
            </div>
            <div class="form-button"><button type="submit" class="button">Submit</button></div>
            <div><router-link to="/">Front page</router-link></div>
        </form>
    </div>
</template>
<script>
export default{
    data() {
        return {
            universities: [],
            colleges: [],
            courses:[],
            name:'',
            dob: new Date().toISOString().slice(0,10),
            qualification:'',
            address:'',
            select_uni:'',
            select_college:'',
            select_course:''
        }
    },
    methods: {
        listUniversities(){
            fetch('http://127.0.0.1:8000/university_options')
            .then((res) => res.json())
            .then((data) => {
                this.universities = data;})
                .catch((err) => console.log(err.message));
        },
        listColleges() {
            if(this.select_uni){
                fetch(`http://127.0.0.1:8000/college_options/${this.select_uni}`)
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                this.colleges = data;})
                .catch((err) => console.log(err.message));
            }
        },
        listCourses() {
            if(this.select_college){
                fetch(`http://127.0.0.1:8000/course_options/${this.select_college}`)
            .then((res) => res.json())
            .then((data) => {
                console.log(data);
                this.courses = data;})
                .catch((err) => console.log(err.message));
            }
        },
        submitForm(){
            const formData = {
                name: this.name,
                dob: this.dob,
                qualification: this.qualification,
                address:this.address,
                uni: this.select_uni,
                college: this.select_college,
                course: this.select_course
            };
            fetch('http://127.0.0.1:8000/create_admission',{
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                        },
                body: JSON.stringify(formData),
            })
            .then((res) => res.json())
            .then((data) => {
                console.log(data.message);
                this.$router.push('/');
            })
            .catch((err) => console.log(err.message));
        }
    },
    created() {
        this.listUniversities();
    }
}
</script>
<style>
.form{
    border: 3px solid;
    border-color: rgb(25, 219, 145);
    border-radius: 3px;
}
.form-element{
    padding: 15px;
}
.form-label{
    font-size:large;
    font-weight: 600;
}
.form-input{
    width: 400px;
    height: 30px;
}
.button{
    font-size: larger;
  background-color: #4AAE9B;
  border-radius: 5px;
  width: max-content;
}
.form-button{
    justify-content: center;
    display:flex;
}
.form-row{
    display:flex;
}
.form-course-row{
    padding-left: 200px;
}
</style>