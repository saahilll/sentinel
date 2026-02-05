package com.sentinel.sentinel_core.model;

import jakarta.persistence.*;
import lombok.Data;
import java.util.UUID;
import java.time.LocalDateTime;

@Data 
@Entity
@Table(name = "users")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String email;

    private String fullName;

    @Column(unique = true)
    private String authProviderId;

    private LocalDateTime createdAt;

    public User() {
        this.createdAt = LocalDateTime.now();
    }
}