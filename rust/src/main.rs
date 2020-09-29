#![allow(non_snake_case)]
#![allow(unused_variables)]

extern crate rand;
extern crate reqwest;
extern crate num;

use std::str::FromStr;
use chrono::prelude::*;

type Error = Box<dyn std::error::Error>;
type Result<T, E = Error> = std::result::Result<T, E>;

async fn login(username: &str, userpasswd: &str) -> Result<()> {
    let response = reqwest::Client::new()
        .post("http://10.1.1.131:901/include/auth_action.php")
        .header("Accepts", "*/*")
        .form(&[("action", "login"), ("username", username), ("password", userpasswd), ("ac_id", "1"), ("save_me", "1"), ("ajax", "1")])
        .send()
        .await?;

    // println!("{}", response.status());

    let result = response.text().await?;
    let split = result.split(",");
    let message: Vec<&str> = split.collect();
    if message[0] == "login_ok" {
        println!("登录成功");
    }

    Ok(())
}

async fn logout(username: &str, userpasswd: &str) -> Result<()> {
    let response = reqwest::Client::new()
        .post("http://10.1.1.131:901/include/auth_action.php")
        .header("Accepts", "*/*")
        .form(&[("action", "logout"), ("username", username), ("password", userpasswd), ("ac_id", "1"), ("save_me", "1"), ("ajax", "1")])
        .send()
        .await?;

    // println!("{}", response.status());

    let message = response.text().await?;

    println!("{}", message);

    Ok(())
}

fn format_time(sec: usize) -> String {
    let h = (sec / 3600) as usize;
    let m = (sec % 3600) as usize;
    let s = sec % 3600 % 60;
    let mut out = String::default();
    if h < 10 {
        out += &format!("0{} : ", h);
    }
    else {
        out += &format!("{} : ", h);
    }
    if m < 10 {
        out += &format!("0{} : ", m);
    }
    else {
        out += &format!("{} : ", m);
    }
    if s < 10 {
        out += &format!("0{}", s);
    }
    else {
        out += &format!("{}", s);
    }
    return out;
}

fn format_number(num: f64, count: usize) -> f64 {
    let n = num::pow::pow(10, count) as f64;
    let t = (num * n) as usize;
    return t as f64 / n;
}

fn format_flux(byte: usize) -> String {
    if byte > (1000 * 1000) {
        return format_number(byte as f64 / (1000.0 * 1000.0), 2).to_string() + &String::from("M");
    }
    if byte > 1000 {
        return format_number(byte as f64 / 1000.0 , 2).to_string() + &String::from("K");
    }
    return byte.to_string() + &String::from("b");
}

async fn getinfo() -> Result<()> {
    use rand::prelude::*;
    let random_val: f64 = rand::thread_rng().gen();
    let key: usize = (random_val * (100000 + 1) as f64) as usize;
    let response = reqwest::Client::new()
        .post("http://10.1.1.131:901/include/auth_action.php")
        .header("Accepts", "*/*")
        .form(&[("action", "get_online_info"), ("key", &key.to_string())])
        .send()
        .await?;

    // println!("{}", response.status());

    let message = response.text().await?;
    let split = message.split(",");
    let online_info: Vec<&str> = split.collect();

    if let Err(ParseIntError) = online_info[0].parse::<usize>() {
        if message == "not_online" {
            println!("当前没有在线账户");
        }
    } else {
        println!("已用流量：{} ",    format_flux(usize::from_str(online_info[0]).unwrap()));
        println!("已用时长：{} ",    format_time(usize::from_str(online_info[1]).unwrap()));
        println!("账户余额：￥{} ",  online_info[2]);
        println!("IP地址：{} ",     online_info[5]);
    }

    Ok(())
}

fn get_hour() -> usize {
    let current_hour: DateTime<Local> = Local::now();
    current_hour.hour() as usize
}

fn check_status(url: &str) -> bool {
    use std::process::Command;
    let status = Command::new("ping")
        .arg(url)
        .output()
        .expect("启动进程失败");
    status.status.success()
}

async fn auto_login(username: &str, userpasswd: &str) -> Result<()> {
    use std::{thread::sleep, time};
    let delay = time::Duration::from_secs(300);
    loop {
        let current_hour = get_hour();
        if current_hour >= 2 && current_hour < 4 {
            if !check_status("www.baidu.com") {
                login(username, userpasswd).await?;
            }
        }
        sleep(delay);
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    use std::env;
    let args: Vec<String> = env::args().collect();
    
    let showhelp = || -> () {
        println!("程序用法： {name} <功能>", name=args[0]);
        println!("功能一览: ");
        println!("  login <用户名> <用户密码> - 登录");
        println!("  logout <用户名> <用户密码> - 注销");
        println!("  info - 显示在线账户信息");
        println!("  autologin - 自动登录进程");
    };

    if args.len() < 2 {
        showhelp();
    } else if args[1] == "login" {
        if args.len() == 4 {
            login(&args[2], &args[3]).await?;
        } else {
            showhelp();
        }
    } else if args[1] == "logout" {
        if args.len() == 4 {
            logout(&args[2], &args[3]).await?;
        } else {
            showhelp();
        }
    } else if args[1] == "info" {
        getinfo().await?;
    } else if args[1] == "autologin" {
        auto_login(&args[2], &args[3]).await?;
    } else {
        showhelp();
    }


    Ok(())
}