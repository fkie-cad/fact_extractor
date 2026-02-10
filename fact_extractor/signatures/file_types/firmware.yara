rule DLink_DCS_FW {
    meta:
        MIME = "firmware/dlink-dcs"
    condition:
        uint32(0x00) == 0xAA7EC55B
}

rule DLink_DCS_FW_ENC {
    meta:
        MIME = "firmware/dlink-dcs-enc"
    condition:
        // we are only looking for encrypted files here
        not DLink_DCS_FW
        // uint32(0x00) = magic_enc, uint32(0x04) = size_enc
        // magic should be 0xAA7EC55B => XOR_key = magic_enc ^ magic
        // size = size_enc ^ XOR_key = size_enc ^ magic_enc ^ magic
        // and size should be equal to filesize - header_size (=16) if the file is in the DCS format
        and uint32(0x04) ^ uint32(0x00) ^ 0xAA7EC55B == filesize - 16
}
