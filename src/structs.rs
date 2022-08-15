use serde::{Deserialize,Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Haber {
    #[serde(with = "bson::serde_helpers::u32_as_f64")]
    pub _id: u32,
    pub title: String,
    pub thumbnail: String,
    pub summary: String,
    pub link: String,
    pub date: Option<[f64;3]>,
    pub content: String
}

#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum SponsorRank {
    Platinium,
    Gold,
    Silver
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Sponsor {
    pub rank: SponsorRank,
    pub name: String,
    pub logo: String,
    pub website: String,
    #[serde(with = "bson::serde_helpers::u32_as_f64")]
    pub year: u32
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Member {
    #[serde(with = "bson::serde_helpers::u32_as_f64")]
    pub _id: u32,
    pub name: String,
    pub surname: String,
    pub role: String,
    pub pfp: String,
    pub desc: String
}
