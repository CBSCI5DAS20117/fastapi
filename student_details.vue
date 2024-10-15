<template>
    <div class="div-table">
        <table>
            <tr>
                <th width="50%">Name</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.name }}</td>
            </tr>
            <tr>
                <th width="50%">Date of Birth</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.dob }}</td>
            </tr>
            <tr>
                <th width="50%">Qualification</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.qualification }}</td>
            </tr>
            <tr>
                <th width="50%">Address</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.address }}</td>
            </tr>
            <tr>
                <th width="50%">Course</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.course }}</td>
            </tr>
            <tr>
                <th width="50%">College</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.college }}</td>
            </tr>
            <tr>
                <th width="50%">University</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.university }}</td>
            </tr>
            <tr>
                <th width="50%">Date of Admission</th>
                <td width="2%">:</td>
                <td width="70%">{{ student_data.date }}</td>
            </tr>
        </table>
    </div>
    <div><RouterLink to="/student_private"><- Go back</RouterLink></div>
</template>
<script>
export default{
    data(){
        return {
            username:localStorage.getItem('username'),
            student_data: '',
        }
    },
    methods:{
        showStudentDetails(){
            fetch(`http://127.0.0.1:8000/student_details/${this.username}`)
            .then((res) => res.json())
            .then((data) => {
                this.student_data = data;})
                .catch((err) => console.log(err.message));
        }
    },
    created(){
        this.showStudentDetails();
    }
}
</script>
<style>
h1{
    font-family:  Georgia, 'Times New Roman', Times, serif;
}
table{
    border: 2px solid;
    width:600px;
    height: 500px;
}
.div-table{
    padding-right: 400px;
}
td,th{
    text-align: center;
    border-bottom: 1px solid #ddd;
}
th{
    background-color: #a5e6ce;
    font-weight: 600;
}
</style>