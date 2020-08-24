var mongoose = require("mongoose");
var passportLocalMongoose = require("passport-local-mongoose");

var UserSchema = new mongoose.Schema({
    username: String,
    cluster: Number,
    prop_1: Number,
    prop_2: Number,
    prop_3: Number
})

UserSchema.plugin(passportLocalMongoose);

module.exports = mongoose.model("User", UserSchema);