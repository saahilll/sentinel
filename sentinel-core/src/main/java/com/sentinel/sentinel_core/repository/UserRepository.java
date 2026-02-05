package com.sentinel.sentinel_core.repository;

import com.sentinel.sentinel_core.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
import java.util.UUID;

public interface UserRepository extends JpaRepository<User, UUID> {
    Optional<User> findByAuthProviderId(String authProviderId);
    Optional<User> findByEmail(String email);
}