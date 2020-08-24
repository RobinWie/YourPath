// CREDENTIALS
const DATABASE = process.env.DATABASE
const YOUTUBE_API_DEVELOPER_KEY = process.env.YOUTUBE_API_DEVELOPER_KEY
const SPOTIFY_API_CLIENT_ID = process.env.SPOTIFY_API_CLIENT_ID
const SPOTIFY_API_CLIENT_SECRET = process.env.SPOTIFY_API_CLIENT_SECRET

// IMPORT MODULES
var express = require("express");
var app = express();
var bodyParser = require("body-parser");
var mongoose = require("mongoose");
var passport = require("passport");
var LocalStrategy = require("passport-local");
var User = require("./models/user")
const spawn = require("child_process").spawn; // for python scripts

// PARSING INPUTS FROM FORMS
app.use(bodyParser.urlencoded({extended: true}));
app.set("view engine", "ejs");

// PARSING AXIOS
app.use(bodyParser.json())

// PASSPORT CONFIGURATION
app.use(require("express-session")({
    secret:"yourpath_secret",
    resave: false,
    saveUninitialized: false
}));
app.use(passport.initialize());
app.use(passport.session());
passport.use(new LocalStrategy(User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());
app.use(function(req, res, next){
    res.locals.currentUser = req.user;
    next();
})

function isLoggedIn(req, res, next){
    if(req.isAuthenticated()){
        return next();
    }
    res.redirect("/login");
}

// CONNECT TO MONGODB
mongoose.connect(DATABASE);

//ROUTES
// PRE AUTHENTICATION ROUTES
app.get("/", function (req, res){
    res.render("home");
})

app.get("/about", function (req, res){
    res.render("about");
})

// AUTHENTICATION ROUTES
// show register form
app.get("/register", function(req, res){
    res.render("register");
})

// handle register logic
app.post("/register", function(req, res){
    //run python script with req.body.keyword -> results
    const ls = spawn('python', ['./backend/get_cluster.py', req.body.question_1, req.body.question_2, req.body.question_3, DATABASE]);
    new_cluster = undefined;
    ls.stdout.on('data', (data) => {
        new_cluster = parseInt(data.toString().charAt(1));
        console.log(new_cluster)
        // console.log(`stdout: ${data}`);
    });
        ls.stderr.on('data', (data) => {
        console.log(`stderr: ${data}`);
    });

    ls.on('close', (code) => {
        console.log(`child process exited with code ${code}`);
    });

    isready = false;
    function wait_then_execute2() {
        if (isready==false) {
            setTimeout(wait_then_execute2, 1000);
        }
        else {
            passport.authenticate("local")(req, res, function(){
                res.redirect("/search");
            });
        }
    }

    function wait_then_execute() {
        if (new_cluster==undefined) {
            setTimeout(wait_then_execute, 1000); // try again in 300 milliseconds
        } 
        else {
            var newUser = new User({username: req.body.username, prop_1: req.body.question_1, prop_2: req.body.question_2, prop_3: req.body.question_3, cluster: new_cluster}); // Add properties here
            User.register(newUser, req.body.password, function(err, user){
                if(err){
                    console.log(err);
                    return res.render("register");
                }

                const ls = spawn('python', ['./backend/add_user_to_cluster.py', req.body.username, new_cluster, DATABASE]);
                ls.stdout.on('data', (data) => {
                    isready = true
                    console.log(`stdout: ${data}`);
                    });
                ls.on('close', (code) => {
                    isready = true
                    console.log(`child process exited with code ${code}`);
                });
                wait_then_execute2();
            });
        }
    }

    wait_then_execute();
})

app.get("/login", function(req, res){
    res.render("login");
})

// handle login logic
app.post("/login", passport.authenticate("local",
{
    successRedirect: "/search", 
    failureRedirect: "/login"
}), function(req, res){
});

// handle logout logic
app.get("/logout", function(req, res){
    req.logout();
    res.redirect("/");
})

// POST AUTHENTICATION ROUTES
app.get("/search", isLoggedIn, function (req, res){
    res.render("search",);
})

app.post("/results", isLoggedIn, function(req, res){
    //run python script with req.body.keyword -> results
    const ls = spawn('python', ['./backend/backend.py', req.user.username, req.body.keyword, DATABASE, YOUTUBE_API_DEVELOPER_KEY, SPOTIFY_API_CLIENT_ID, SPOTIFY_API_CLIENT_SECRET]);
    
    ls.stdout.on('data', (data) => {
    res.render("show", {results: data});
    //console.log(`stdout: ${data}`);
    });
    ls.stderr.on('data', (data) => {
    console.log(`stderr: ${data}`);
    });

    ls.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    });
})

// LIKE ROUTES
app.post("/like", function (req, res) {
    //run python script with req.body
    const ls = spawn('python', ['./backend/add_rec_to_cluster.py', req.body.cluster_id, req.body.rec_id, req.body.platform, DATABASE]);
    
    ls.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
    });
    ls.stderr.on('data', (data) => {
    console.log(`stderr: ${data}`);
    });

    ls.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
    });
})

// RUN SERVER
var port = process.env.PORT || 3000;
app.listen(port, function () {
    console.log("Server Has Started!");
});