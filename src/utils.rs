use crate::structs::{Sponsor, SponsorRank};

pub fn get_page_range(document_per_page: i32, document_count: i32, page: i32) -> Vec<i32> {
    let mut i = document_count-(document_per_page*page);
    let mut ids_list = Vec::<i32>::new();
    while i<(document_count-(document_per_page*(page-1))) {
        i += 1;
        ids_list.push(i);
    }
    ids_list
}

pub async fn cursor_collect<T: serde::de::DeserializeOwned>(cursor: &mut mongodb::Cursor<T>) -> Result<Vec<T>, mongodb::error::Error> {
    let mut collection: Vec<T> = Vec::new();
    while cursor.advance().await? {
        collection.push(cursor.deserialize_current()?);
    }
    Ok(collection)
}

pub fn date_to_human_date(input: [f64;3]) -> String {
    const MONTHS: [&str; 12] = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
    format!("{} {} {}", input[0] as u8, MONTHS[input[1] as usize], input[2] as u16)
}

pub fn group_sponsors(sponsors: Vec<Sponsor>) -> (Vec<u32>, Vec<Vec<Vec<Sponsor>>>) {
    let mut sponsors_grouped = Vec::<Vec<Vec<Sponsor>>>::new();
    let mut years = Vec::<u32>::new();
    for sponsor in &sponsors {
        if !years.contains(&sponsor.year){
            years.push(sponsor.year);
        }
    }
    let mut i = 0;
    for _ in &years {
        sponsors_grouped.push(Vec::new());
        sponsors_grouped[i].push(Vec::new());
        sponsors_grouped[i].push(Vec::new());
        sponsors_grouped[i].push(Vec::new());
        sponsors.iter()
            .filter(|x| x.year == years[i])
            .for_each(|x| {
                match x.rank{
                    SponsorRank::Platinium => sponsors_grouped[i][0].push(x.clone()),
                    SponsorRank::Gold => sponsors_grouped[i][1].push(x.clone()),
                    SponsorRank::Silver => sponsors_grouped[i][2].push(x.clone()),
                }
            });
        i += 1;
    }
    (years, sponsors_grouped)
}
